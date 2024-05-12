# %%
import pandas as pd



# %%
df = pd.read_csv('covid.csv', sep=',')

# Renomeando colunas
nomes = {
    'USMER': 'usmr',
    'MEDICAL_UNIT': 'unidade_medica',
    'SEX': 'sexo',
    'PATIENT_TYPE': 'tipo_paciente',
    'DATE_DIED': 'data_obito',
    'INTUBED': 'intubado',
    'PNEUMONIA': 'pneumonia',
    'AGE': 'idade',
    'PREGNANT': 'gravidez',
    'DIABETES': 'diabetes',
    'COPD': 'doenca_pulmonar_obstrutiva',
    'ASTHMA': 'asma',
    'INMSUPR': 'imunossuprimido',
    'HIPERTENSION': 'hipertensao',
    'OTHER_DISEASE': 'outras_doencas',
    'CARDIOVASCULAR': 'doenca_cardiovascular',
    'OBESITY': 'obesidade',
    'RENAL_CHRONIC': 'doenca_renal_cronica',
    'TOBACCO': 'fumante',
    'CLASIFFICATION_FINAL': 'teste_covid',
    'ICU':'uti'
}

df = df.rename(columns=nomes)

# Renomeando categorias
categoria_bool = {
    1: 'Sim',
    2: 'Não',
    97: 'Não registrado',
    98: 'Não registrado',
    99: 'Não registrado'
}

categoria_sexo = {
    1: 'M',
    2: 'H'
}

categoria_paciente = {
    1: 'Retornou para casa',
    2: 'Hospitalizado'
}

categoria_teste_covid = {
    1: 'Paciente diagnosticado',
    2: 'Paciente diagnosticado',
    3: 'Paciente diagnosticado',
    4: 'Não contaminado/Teste inconclusivo',
    5: 'Não contaminado/Teste inconclusivo',
    6: 'Não contaminado/Teste inconclusivo',
    7: 'Não contaminado/Teste inconclusivo'
}

datas = {
    '9999-99-99': '01/01/1900' # Substitui o padrão de data de não óbito por um modelo que facilita a correção de tipagem
}

bool_cols = ['intubado', 'pneumonia',
             'gravidez', 'diabetes',
             'doenca_pulmonar_obstrutiva',
             'asma', 'imunossuprimido',
             'hipertensao','outras_doencas',
             'doenca_cardiovascular',
             'obesidade','doenca_renal_cronica',
             'fumante', 'uti']

df[bool_cols] = df[bool_cols].replace(categoria_bool)
df['sexo'] = df['sexo'].replace(categoria_sexo)
df['tipo_paciente'] = df['tipo_paciente'].replace(categoria_paciente)
df['teste_covid'] = df['teste_covid'].replace(categoria_teste_covid)
df['data_obito'] = df['data_obito'].replace(datas)


# Tipagem de dados
df['data_obito'] = pd.to_datetime(df['data_obito'], format='%d/%m/%Y')

# Criando uma coluna de ID
df['id_paciente'] = df.index.astype(str) + '_' + df['sexo']

df.head(3)



# %%
tipos = df.dtypes
tipos[tipos == 'int64'].index

# Verifica se há homens com registros de gravidez
mask_grav_homem = (df['sexo'] == 'H') & (df['gravidez'] != 'Não registrado')
display(print(f'Homens com registro de gravidez: {df[mask_grav_homem].shape[0]}'))

# Verifica se há "não registrado" na coluna de gravidez para homens
mask_grav_nao_reg = df['gravidez'] == 'Não registrado'
display(df[mask_grav_nao_reg]['sexo'].value_counts())

mapping = {
    'Não registrado': 'Paciente sexo masculino'
}

mask_grav_homem_nao_reg = (df['sexo'] == 'H') & (df['gravidez'] != 'Não registrado')
df.loc[mask_grav_homem_nao_reg, 'gravidez'] = df.loc[mask_grav_homem_nao_reg, 'gravidez'].replace(mapping)

display(df['gravidez'][df['sexo'] == 'H'].value_counts())



# %%
mask_2 = df['tipo_paciente'] == 'Retornou para casa'

for coluna in ['uti', 'intubado']:
    print('-------------')
    print(df[mask_2][coluna].value_counts())



# %%
substituir = {
    'Não registrado':'Paciente não hospitalizado'
}

df.loc[mask_2, ['uti', 'intubado']] = df.loc[mask_2, ['uti', 'intubado']].replace(substituir)

for coluna in ['uti', 'intubado']:
    print('-------------')
    print(df[mask_2][coluna].value_counts())



# %%

# PERGUNTAS
# Como deu-se a evolução dos óbitos? Foi linear ou tivemos períodos de picos e controles?

# Nos períodos com mais óbitos, podemos isolar os pacientes e ver qual predisposição de saúde foi mais presente?

# Qual o percentual de pacientes não hospitalizados faleceram?

# Nos períodos de maior número de óbitos, há muitos pacientes não hospitalizados?



# %%
import matplotlib.pyplot as plt

# %%
# Como deu-se a evolução dos óbitos? Foi linear ou tivemos períodos de picos e controles?

mask_sobr = df['data_obito'] != '1900-01-01'

df['ano_obito'] = df['data_obito'].dt.year
df['mes_obito'] = df['data_obito'].dt.month

group_obt = df[['id_paciente', 'ano_obito', 'mes_obito']][mask_sobr].groupby(by=['ano_obito', 'mes_obito']).count()
group_obt = group_obt.reset_index()


periodo = [f'{ano}-{mes}' for ano, mes in zip(group_obt['ano_obito'], group_obt['mes_obito'])]
periodo

fig, ax = plt.subplots(figsize=(10,5))
ax.bar(x=periodo, height=group_obt['id_paciente'])
ax.set_title('Evolução de óbitos')
ax.set_xlabel('Período')
ax.set_ylabel('Num. de óbitos')

plt.xticks(rotation=45, ha='right')

plt.show()


# %%

# Nos períodos com mais óbitos, podemos isolar os pacientes e ver qual predisposição de saúde foi mais presente?

mask_maior_obt = (df['data_obito'] >= '2020-04-01') & (df['data_obito'] <= '2020-08-31')
pred = ['pneumonia', 'diabetes',
       'doenca_pulmonar_obstrutiva', 'asma', 'imunossuprimido', 'hipertensao',
       'outras_doencas', 'doenca_cardiovascular', 'obesidade',
       'doenca_renal_cronica', 'fumante']

print(f'Óbitos no periodo: {df[mask_maior_obt].shape[0]}')

for coluna in pred:
    print('---',coluna,'---')
    print(df[coluna][mask_maior_obt].value_counts())
    print('----------------------')


# %%
# Qual o percentual de pacientes não hospitalizados faleceram?

total_nao_hosp = df[df['tipo_paciente'] == 'Retornou para casa'].shape[0]
total_nao_hosp

mask_faleceu_nao_hosp = (df['tipo_paciente'] == 'Retornou para casa') & (df['data_obito'] != '1900-01-01')
obt_nao_hosp = df[mask_faleceu_nao_hosp].shape[0]
obt_nao_hosp

print(f'Pacientes não hospitalizados que faleceram: {obt_nao_hosp}.\nTotalizando {round(obt_nao_hosp/total_nao_hosp*100,2)}% dos {total_nao_hosp} não hospitalizados.')

# %%
# Nos períodos de maior número de óbitos, há muitos pacientes não hospitalizados?

total_periodo = df[mask_maior_obt].shape[0]
n_hosp = df[mask_maior_obt][df['tipo_paciente'] == 'Retornou para casa'].shape[0]

print(f'Pacientes não hospitalizados durante o período de maior números de óbitos: {n_hosp}.\nTotal de registros no periodo: {total_periodo}.')