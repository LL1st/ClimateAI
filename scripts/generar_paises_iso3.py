"""Genera data/processed/paises_iso3.csv (pais, iso3) para los 232 países del dataset.

Uso: python scripts/generar_paises_iso3.py

Los nombres vienen de Berkeley Earth (en inglés, con algunas variantes propias). No usa
internet ni librerías extra: la tabla de códigos ISO 3166-1 alfa-3 está escrita aquí.
Los territorios sin código propio quedan con iso3 vacío y se listan al final.
"""
import os
import re
import sys

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRADA = os.path.join(RAIZ, 'data', 'processed', 'clima_pais_anio.csv')
SALIDA = os.path.join(RAIZ, 'data', 'processed', 'paises_iso3.csv')

# Nombres en inglés estándar (coinciden con el nombre corto habitual del país).
ESTANDAR = {
    'Afghanistan': 'AFG', 'Albania': 'ALB', 'Algeria': 'DZA', 'American Samoa': 'ASM', 'Andorra': 'AND',
    'Angola': 'AGO', 'Anguilla': 'AIA', 'Argentina': 'ARG', 'Armenia': 'ARM', 'Aruba': 'ABW',
    'Australia': 'AUS', 'Austria': 'AUT', 'Azerbaijan': 'AZE', 'Bahamas': 'BHS', 'Bahrain': 'BHR',
    'Bangladesh': 'BGD', 'Barbados': 'BRB', 'Belarus': 'BLR', 'Belgium': 'BEL', 'Belize': 'BLZ',
    'Benin': 'BEN', 'Bhutan': 'BTN', 'Botswana': 'BWA', 'Brazil': 'BRA', 'British Virgin Islands': 'VGB',
    'Bulgaria': 'BGR', 'Burkina Faso': 'BFA', 'Burundi': 'BDI', 'Cambodia': 'KHM', 'Cameroon': 'CMR',
    'Canada': 'CAN', 'Cayman Islands': 'CYM', 'Central African Republic': 'CAF', 'Chad': 'TCD',
    'Chile': 'CHL', 'China': 'CHN', 'Christmas Island': 'CXR', 'Colombia': 'COL', 'Comoros': 'COM',
    'Costa Rica': 'CRI', 'Croatia': 'HRV', 'Cuba': 'CUB', 'Curaçao': 'CUW', 'Cyprus': 'CYP',
    'Denmark': 'DNK', 'Djibouti': 'DJI', 'Dominica': 'DMA', 'Dominican Republic': 'DOM', 'Ecuador': 'ECU',
    'Egypt': 'EGY', 'El Salvador': 'SLV', 'Equatorial Guinea': 'GNQ', 'Eritrea': 'ERI', 'Estonia': 'EST',
    'Ethiopia': 'ETH', 'Faroe Islands': 'FRO', 'Fiji': 'FJI', 'Finland': 'FIN', 'France': 'FRA',
    'French Guiana': 'GUF', 'French Polynesia': 'PYF', 'Gabon': 'GAB', 'Gambia': 'GMB', 'Georgia': 'GEO',
    'Germany': 'DEU', 'Ghana': 'GHA', 'Greece': 'GRC', 'Greenland': 'GRL', 'Grenada': 'GRD',
    'Guadeloupe': 'GLP', 'Guam': 'GUM', 'Guatemala': 'GTM', 'Guernsey': 'GGY', 'Guinea': 'GIN',
    'Guyana': 'GUY', 'Haiti': 'HTI', 'Honduras': 'HND', 'Hong Kong': 'HKG', 'Hungary': 'HUN',
    'Iceland': 'ISL', 'India': 'IND', 'Indonesia': 'IDN', 'Iraq': 'IRQ', 'Ireland': 'IRL', 'Israel': 'ISR',
    'Italy': 'ITA', 'Jamaica': 'JAM', 'Japan': 'JPN', 'Jersey': 'JEY', 'Jordan': 'JOR',
    'Kazakhstan': 'KAZ', 'Kenya': 'KEN', 'Kiribati': 'KIR', 'Kuwait': 'KWT', 'Kyrgyzstan': 'KGZ',
    'Latvia': 'LVA', 'Lebanon': 'LBN', 'Lesotho': 'LSO', 'Liberia': 'LBR', 'Libya': 'LBY',
    'Liechtenstein': 'LIE', 'Lithuania': 'LTU', 'Luxembourg': 'LUX', 'Madagascar': 'MDG', 'Malawi': 'MWI',
    'Malaysia': 'MYS', 'Mali': 'MLI', 'Malta': 'MLT', 'Martinique': 'MTQ', 'Mauritania': 'MRT',
    'Mauritius': 'MUS', 'Mayotte': 'MYT', 'Mexico': 'MEX', 'Monaco': 'MCO', 'Mongolia': 'MNG',
    'Montenegro': 'MNE', 'Montserrat': 'MSR', 'Morocco': 'MAR', 'Mozambique': 'MOZ', 'Namibia': 'NAM',
    'Nepal': 'NPL', 'Netherlands': 'NLD', 'New Caledonia': 'NCL', 'New Zealand': 'NZL',
    'Nicaragua': 'NIC', 'Niger': 'NER', 'Nigeria': 'NGA', 'Niue': 'NIU', 'Northern Mariana Islands': 'MNP',
    'Norway': 'NOR', 'Oman': 'OMN', 'Pakistan': 'PAK', 'Palau': 'PLW', 'Panama': 'PAN',
    'Papua New Guinea': 'PNG', 'Paraguay': 'PRY', 'Peru': 'PER', 'Philippines': 'PHL', 'Poland': 'POL',
    'Portugal': 'PRT', 'Puerto Rico': 'PRI', 'Qatar': 'QAT', 'Romania': 'ROU', 'Rwanda': 'RWA',
    'Saint Lucia': 'LCA', 'Saint Martin': 'MAF', 'Samoa': 'WSM', 'San Marino': 'SMR',
    'Saudi Arabia': 'SAU', 'Senegal': 'SEN', 'Serbia': 'SRB', 'Seychelles': 'SYC', 'Sierra Leone': 'SLE',
    'Singapore': 'SGP', 'Sint Maarten': 'SXM', 'Slovakia': 'SVK', 'Slovenia': 'SVN',
    'Solomon Islands': 'SLB', 'Somalia': 'SOM', 'South Africa': 'ZAF', 'Spain': 'ESP',
    'Sri Lanka': 'LKA', 'Sudan': 'SDN', 'Suriname': 'SUR', 'Sweden': 'SWE', 'Switzerland': 'CHE',
    'Tajikistan': 'TJK', 'Thailand': 'THA', 'Togo': 'TGO', 'Tonga': 'TON', 'Tunisia': 'TUN',
    'Turkey': 'TUR', 'Turkmenistan': 'TKM', 'Uganda': 'UGA', 'Ukraine': 'UKR',
    'United Arab Emirates': 'ARE', 'United Kingdom': 'GBR', 'United States': 'USA', 'Uruguay': 'URY',
    'Uzbekistan': 'UZB', 'Western Sahara': 'ESH', 'Yemen': 'YEM', 'Zambia': 'ZMB', 'Zimbabwe': 'ZWE',
}

# Nombres no estándar de Berkeley Earth: nombres antiguos, cortos, con errores o recortados.
EQUIVALENCIAS = {
    'Antigua And Barbuda': 'ATG',
    'Bolivia': 'BOL',                                       # Estado Plurinacional de Bolivia
    'Bonaire, Saint Eustatius And Saba': 'BES',
    'Bosnia And Herzegovina': 'BIH',
    'Burma': 'MMR',                                         # Myanmar
    'Cape Verde': 'CPV',                                    # Cabo Verde
    'Congo': 'COG',                                         # República del Congo
    'Congo (Democratic Republic Of The)': 'COD',
    'Czech Republic': 'CZE',                                # Chequia
    "Côte D'Ivoire": 'CIV',
    'Falkland Islands (Islas Malvinas)': 'FLK',
    'Federated States Of Micronesia': 'FSM',
    'French Southern And Antarctic Lands': 'ATF',
    'Guinea Bissau': 'GNB',
    'Heard Island And Mcdonald Islands': 'HMD',
    'Iran': 'IRN',
    'Isle Of Man': 'IMN',
    'Laos': 'LAO',
    'Macau': 'MAC',
    'Macedonia': 'MKD',                                     # Macedonia del Norte
    'Moldova': 'MDA',
    'North Korea': 'PRK',
    'Palestina': 'PSE',                                     # Cisjordania en Berkeley Earth
    'Reunion': 'REU',
    'Russia': 'RUS',
    'Saint Barthélemy': 'BLM',
    'Saint Kitts And Nevis': 'KNA',
    'Saint Pierre And Miquelon': 'SPM',
    'Saint Vincent And The Grenadines': 'VCT',
    'Sao Tome And Principe': 'STP',
    'South Georgia And The South Sandwich Isla': 'SGS',     # nombre recortado en el CSV original
    'South Korea': 'KOR',
    'Svalbard And Jan Mayen': 'SJM',
    'Swaziland': 'SWZ',                                     # Esuatini
    'Syria': 'SYR',
    'Taiwan': 'TWN',
    'Tanzania': 'TZA',
    'Timor Leste': 'TLS',
    'Trinidad And Tobago': 'TTO',
    'Turks And Caicas Islands': 'TCA',                      # "Caicas": error de origen (Caicos)
    'Venezuela': 'VEN',
    'Vietnam': 'VNM',
    'Virgin Islands': 'VIR',                                # Islas Vírgenes de EE. UU.
    'Åland': 'ALA',
}

# Sin código propio: quedan fuera del mapa, pero siguen en el dataset y en las gráficas.
SIN_CODIGO = {
    'Baker Island': 'deshabitada; parte de las Islas Ultramarinas Menores de EE. UU. (UMI)',
    'Kingman Reef': 'deshabitado; parte de las Islas Ultramarinas Menores de EE. UU. (UMI)',
    'Palmyra Atoll': 'deshabitado; parte de las Islas Ultramarinas Menores de EE. UU. (UMI)',
    'Gaza Strip': 'comparte el código PSE con Palestina; en el mapa se pinta como Palestina',
}


def construir_tabla(paises):
    """Devuelve (DataFrame pais/iso3 en el orden de `paises`, lista de nombres desconocidos)."""
    codigos = {**ESTANDAR, **EQUIVALENCIAS}
    desconocidos = [p for p in paises if p not in codigos and p not in SIN_CODIGO]
    filas = [{'pais': p, 'iso3': codigos.get(p, '')} for p in paises]
    return pd.DataFrame(filas), desconocidos


def validar(tabla):
    con_codigo = tabla[tabla.iso3 != '']
    malos = con_codigo[~con_codigo.iso3.str.fullmatch(r'[A-Z]{3}')]
    repetidos = con_codigo[con_codigo.iso3.duplicated(keep=False)]
    return malos, repetidos


def main():
    paises = sorted(pd.read_csv(ENTRADA, encoding='utf-8').pais.unique())
    tabla, desconocidos = construir_tabla(paises)
    malos, repetidos = validar(tabla)
    if desconocidos or not malos.empty or not repetidos.empty:
        print('ERROR · nombres sin entrada en la tabla:', desconocidos)
        print('ERROR · códigos mal formados:', malos.to_dict('records'))
        print('ERROR · códigos repetidos:', repetidos.to_dict('records'))
        sys.exit(1)
    tabla.to_csv(SALIDA, index=False, encoding='utf-8')
    sin = tabla[tabla.iso3 == '']
    print(f'{len(tabla)} países · {len(tabla) - len(sin)} con ISO3 · {len(sin)} sin código -> {os.path.relpath(SALIDA, RAIZ)}')
    print('\nPaíses sin código (quedan fuera del mapa):')
    for p in sin.pais:
        print(f'  - {p}: {SIN_CODIGO[p]}')


if __name__ == '__main__':
    main()
