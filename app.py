import pandas as pd
import assets.consulta as consulta

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import dash_table

activos = consulta.get_solicitudes_activas()
activos.grupo.fillna('Indeterminado',inplace=True)

activos_dic = {activos.id_.iloc[i] : (activos.certificado.iloc[i],
                                      list(activos.loc[activos.certificado == activos.certificado.iloc[i]].sol_id.unique()),
                                      list(activos.loc[activos.certificado == activos.certificado.iloc[i]].persona.unique())) for i in range(len(activos))}

opciones_filtrado = {'Certificado':'certificado',
                     'Grupo':'grupo',
                     'Estado':'estado_actual',
                     'Solicitud':'nro_solicitud'}


#------------------------------------------------------------------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# instanciamos la app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

# le definimos un título
app.title = 'Estado de Titulaciones de POSGRADOS'
# instanciamos el servidor
server = app.server  # the Flask app

freedb = pd.DataFrame()
################################## APP SETTING ###############################
################################## APP LAYOUT ################################
app.layout = html.Div([
    # genero la misma cabecera que las otras apps
    html.Div(className='row',
             children=[
                 html.H4('Estado de Titulaciones de POSGRADOS', className='eight columns'),
                 html.Img(src='/assets/untref_logo.jpg',
                          className='four columns',
                          style={'margin-top': '13px'}),
                 ]
             ),
    # inserto una linea de separacion
    html.Div(style={'margin-bottom':'-20px','margin-top':'-20px'},children =[html.Hr()]),

    # generamos un selector de filtro
    html.Div(className='row cuerpo',
             style={'margin-bottom': '5px'},
             children=[
                 html.Label(children='Seleccione un criterio de filtrado:',
                            className='row'),
                 dcc.RadioItems(
                     id='filtro-elegido',
                     options=[{'label': k, 'value': k} for k in opciones_filtrado],
                     value='Certificado',
                     labelStyle={'display': 'inline-block', 'margin-right': '15px'},
                 )
             ]),

    # nos muestra la opcion del filtro elegido
    html.Div(className='row cuerpo',
             children = [
                 html.Div(id='elemento-filtrado',
                          children=[
                              # creo uno falso para evitar la falla del callback
                              html.Div(hidden=True,children=dcc.Input(id='dropdown-filtro'),)
                          ]),
                        ]
             ),

    # inserto una linea de separacion
    html.Div(style={'margin-bottom': '-20px', 'margin-top': '-15px'}, children=[html.Hr()]),

    # segun el elemento filtrado
    html.Div(className='row cuerpo',
             children=[
                 # establecemos el título según lo filtrado.
                 html.H5(id='detalle-solicitudes-titulo'),
                 html.P(id='detalle-solicitudes-cantidad'),

                # vemos las solicitudes, filtradas o no
                dash_table.DataTable(id='tabla-solicitudes',
                                     row_selectable='single',
                                     include_headers_on_copy_paste=True,
                                     row_deletable=True,
                                     style_header={
                                         'backgroundColor': 'rgb(230, 230, 230)',
                                         'fontWeight': 'bold'
                                     },
                                     style_cell_conditional = [
                                        {
                                            'if': {'column_id': 'Solicitud'},
                                            'textAlign': 'center',
                                            'fontWeight': 'bold'
                                        },
                                        {
                                            'if': {'column_id': 'Grupo'},
                                            'textAlign': 'center',
                                            'fontWeight': 'bold',
                                            'minWidth': '70px',
                                        },
                                    ],
                                    style_cell = {
                                                     'whiteSpace': 'normal',
                                                     'height': 'auto',
                                                     'textAlign': 'left',
                                                 },
                                    ),
                 ]
             ),

    # inserto una linea de separacion
    html.Div(style={'margin-bottom': '-20px', 'margin-top': '-15px'}, children=[html.Hr()]),

    # finalmente muestro los datos de la solicitud, junto a los datos de la persona y la documentación presentada
    html.Div(id='div-solicitud-elegida',
             className='datos cuerpo',
             children=[
                 # div de estados
                 html.Div(className='cajasdatos',
                          children = [html.Label(id='nro-solicitud-elegida'),
                                      dash_table.DataTable(
                                          id='tabla-sol-elegida',
                                          style_cell={
                                              'whiteSpace': 'normal',
                                              'height': 'auto',
                                              'textAlign': 'left',
                                              },
                                          style_header={
                                              'backgroundColor': 'rgb(230, 230, 230)',
                                              'fontWeight': 'bold'
                                              },
                                          )
                                      ]
                          ),

                 # div de datos de la persona
                 html.Div(className='cajasdatos',
                          children = [html.Label(id='persona-elegida'),
                                      dash_table.DataTable(
                                          id='tabla-per-elegida',
                                          style_cell={
                                              'whiteSpace': 'normal',
                                              'height': 'auto',
                                              'textAlign': 'left',
                                              },
                                          style_header={
                                              'backgroundColor': 'rgb(230, 230, 230)',
                                              'fontWeight': 'bold'
                                              },
                                          )
                                      ]
                          ),

                 # div de datos de la persona
                 html.Div(className='row cajasdatos',
                          children=[
                     html.Div(className='five columns cajasdatos',
                              children=[
                                  html.Label(id='solicitud-elegida-datos'),

                                  dash_table.DataTable(
                                      id='tabla-datos-sol-elegida',
                                      style_cell={
                                          'whiteSpace': 'normal',
                                          'height': 'auto',
                                          'textAlign': 'left',
                                          },
                                      style_header={
                                          'backgroundColor': 'rgb(230, 230, 230)',
                                          'fontWeight': 'bold'
                                          },
                                      )
                              ]
                              ),

                     # div de documentacion presentada
                     html.Div(className='four columns cajasdatos',
                              children=[html.Label(id='solicitud-elegida-documentacion'),
                                        dash_table.DataTable(
                                            id='tabla-datos-sol-documentacion',
                                            style_cell={
                                                'whiteSpace': 'normal',
                                                'height': 'auto',
                                                'textAlign': 'left',
                                                },
                                            style_header={
                                                'backgroundColor': 'rgb(230, 230, 230)',
                                                'fontWeight': 'bold'
                                                },
                                            )
                                        ]
                              )
                     ]
                 )
                 ]
             )
    ], className='cuerpo',
)

################################ APP LAYOUT ##################################
################################ CALL BACKS ##################################
@app.callback(
            Output('elemento-filtrado', 'children'),
            Input('filtro-elegido', 'value')
)
def set_filtro(filtro_elegido):
    c = list(activos.certificado.unique())
    e = list(activos.estado.unique())
    g = list(activos.grupo.unique())
    c.sort() ; e.sort()

    if filtro_elegido == 'Certificado':
        return_filtro = dcc.Dropdown(id='dropdown-filtro', options=[dict({'label': c[i], 'value': c[i]}) for i in range(len(c))],
                                     placeholder='seleccione una carrera')
    elif filtro_elegido == 'Grupo':
        return_filtro = dcc.Dropdown(id='dropdown-filtro', options=[dict({'label': g[i], 'value': g[i]}) for i in range(len(g))],
                                     placeholder='seleccione un grupo')
    elif filtro_elegido == 'Estado':
        return_filtro = dcc.Dropdown(id='dropdown-filtro', options=[dict({'label': e[i], 'value': e[i]}) for i in range(len(e))],
                                     placeholder='seleccione un estado')
    elif filtro_elegido == 'Solicitud':
        return_filtro = dcc.Input(id='dropdown-filtro', className='six columns', autoFocus=True, type='number',
                                  placeholder='ingrese un nro de solicitud')

    return [return_filtro]

@app.callback(
    [
        Output('tabla-solicitudes', 'data'),
        Output('tabla-solicitudes', 'columns'),
        Output('nro-solicitud-elegida','children'),
        Output('persona-elegida','children'),
        Output('detalle-solicitudes-titulo','children'),
        Output('detalle-solicitudes-cantidad','children'),
    ],
    [
        Input('filtro-elegido', 'value'),
        Input('dropdown-filtro','value'),
        Input('tabla-solicitudes', 'derived_virtual_selected_rows'),
    ],
)
def set_solicitudes_table(filtro_elegido,elemento_filtrado,fila):
    totales = consulta.get_solicitudes_filtradas(nros_solicitud=list(activos.sol_id.unique()))
    totales.grupo.fillna('Indeterminado',inplace=True)

    if elemento_filtrado == None:
        filtrados = totales.copy()
        cantidad = filtrados.shape[0]
        titulo = 'Solicitudes totales'
    else:
        if filtro_elegido == 'Certificado':
            filtrados = totales.loc[totales.certificado == elemento_filtrado]
            cantidad = filtrados.shape[0]
            titulo = f'Solicitudes de {elemento_filtrado}'
        elif filtro_elegido == 'Grupo':
            matches = []
            for i in totales.grupo:
                if str(elemento_filtrado) in str(i):
                    matches.append(i)
            filtrados = totales.loc[totales.grupo.isin(matches)]
            cantidad = filtrados.shape[0]
            titulo = f'Solicitudes del grupo: {elemento_filtrado}'
        elif filtro_elegido == 'Solicitud':
            matches = []
            for i in totales.nro_solicitud:
                if str(elemento_filtrado) in str(i):
                    matches.append(i)
            filtrados = totales.loc[totales.nro_solicitud.isin(matches)]
            cantidad = filtrados.shape[0]
            titulo = f'Solicitud {elemento_filtrado}'
        elif filtro_elegido == 'Estado':
            matches = []
            for i in totales.estado_actual:
                if str(elemento_filtrado) in str(i):
                    matches.append(i)
            filtrados = totales.loc[totales.estado_actual.isin(matches)]
            cantidad = filtrados.shape[0]
            titulo = f'Solicitudes en estado: {elemento_filtrado}'

    try:
        solicitud = 'Solicitud Nro: '+str(filtrados.nro_solicitud.iloc[fila].iloc[0])
        persona = 'Persona ID: '+str(filtrados.persona.iloc[fila].iloc[0])
    except:
        solicitud = 'Seleccione una solicitud'
        persona = ''

    # harcodeamos algunas columnas y reacomodamos los titulos
    filtrados = filtrados.drop(['fecha_egreso','circuito','persona','nro_documento'],axis=1)
    filtrados = filtrados.rename(columns = {'nro_solicitud': 'Solicitud', 'apellido': 'Apellido', 'nro_documento': 'Nro Documento',
                                            'fecha_inicio_tramite': 'Inicio', 'certificado': 'Certificado', 'nombre_plan': 'Plan',
                                            'circuito': 'Circuito', 'nro_expediente': 'Expediente', 'fecha_egreso': 'Fecha Egreso',
                                            'estado_actual': 'Estado Actual', 'observaciones': 'Observaciones', 'fecha_cambio_estado': 'Ultimo Cambio',
                                            'grupo':'Grupo'})
    if cantidad == 1:
        texto_cantidad = f'Se muestra {cantidad} solicitud'
    else:
        texto_cantidad = f'Se muestran {cantidad} solicitudes'
    return [
        filtrados.to_dict('records'),
        [{"name": i, "id": i} for i in filtrados.columns],
        solicitud,
        persona,
        titulo,
        texto_cantidad
            ]

@app.callback(
    [
        Output('tabla-sol-elegida', 'data'),
        Output('tabla-sol-elegida', 'columns'),
    ],
    [
        Input('tabla-solicitudes', 'derived_virtual_selected_rows'),
        Input('nro-solicitud-elegida', 'children'),
    ],
)
def solicitud_seleccionada(fila,sol_selected):
    db = pd.DataFrame()

    if type(sol_selected) == str:
        if sol_selected == 'Seleccione una solicitud':
            sol_selected = ''
        else:
            sol_selected = int(sol_selected.strip('Solicitud Nro: '))

    if len(str(sol_selected)) > 0:
        db = consulta.get_estados_solicitud(solicitud=sol_selected)
        db = db.rename(columns = {'fecha_cambio':'Fecha','estado_anterior':'Estado Anterior',
                                                            'accion':'Accion','estado_nuevo':'Estado Nuevo',
                                                            'observaciones':'Observaciones','auditoria_usuario':'Usuario'})
    return [
        db.to_dict('records'),
        [{"name": i, "id": i} for i in db.columns],
        ]


@app.callback(
    [
        Output('tabla-per-elegida', 'data'),
        Output('tabla-per-elegida', 'columns'),
    ],
    [
        Input('tabla-solicitudes', 'derived_virtual_selected_rows'),
        Input('persona-elegida', 'children'),
    ],
)
def persona_seleccionada(fila, persona_elegida):

    if persona_elegida == '':
        pass
    else:
        persona_elegida = persona_elegida.strip('Persona ID:')

    db = pd.DataFrame()

    if len(str(persona_elegida)) > 0:
        db = consulta.get_datos_persona(persona=persona_elegida)
        db = db.rename(columns={'apellido':'Apellido','nombres':'Nombres','sexo':'Sexo',
                                        'fecha_nacimiento':'Fecha de Nacimiento','nacionalidad':'Nacionalidad',
                                        'pais_origen':'País de Origen','tipo_doc':'Tipo','nro_documento':'Nro Documento',
                                        'pais_emisor':'País Emisor','institucion_ant':'Institución Anterior',
                                        'titulo_ant':'Título Anterior','f_egreso_ant':'Fecha de Egreso'})
    return [
        db.to_dict('records'),
        [{"name": i, "id": i} for i in db.columns],
    ]

@app.callback(
    [
        Output('tabla-datos-sol-elegida', 'data'),
        Output('tabla-datos-sol-elegida', 'columns'),
        Output('solicitud-elegida-datos', 'children'),
    ],
    [
        Input('tabla-solicitudes', 'derived_virtual_selected_rows'),
        Input('nro-solicitud-elegida', 'children'),
    ],
)
def solicitud_seleccionada_datos(fila,sol_selected):
    db = pd.DataFrame()
    tit = ''

    if type(sol_selected) == str:
        if sol_selected == 'Seleccione una solicitud':
            sol_selected = ''
        else:
            sol_selected = int(sol_selected.strip('Solicitud Nro: '))
            tit = 'Datos ingresados en la solicitud:'

    if len(str(sol_selected)) > 0:
        db = consulta.get_datos_solicitud(solicitud=sol_selected)

        db.fillna('',inplace=True)
        db = db.rename(columns = {'id_solicitud': 'Nro Solicitud', 'fecha_inicio': 'Fecha Inicio', 'resolucion_nro': 'Nro Resolución',
                                  'resolucion_fecha': 'Fecha Resolución', 'resolucion_untref': 'Res UNTREF',
                                  'resolucion_rme': 'Res RME', 'coneau': 'Res CONEAU', 'registro_libro': 'Libro',
                                  'registro_folio': 'Folio', 'registro_orden': 'Orden', 'fecha_egreso': 'Egreso',
                                  'fecha_emision': 'Emisión Diploma', 'nro_solicitud_sidcer': 'Nro SIDCER',
                                  'nro_diploma': 'Nro Diploma', 'fecha_finalizacion_sidcer': 'Finalización SIDCER',
                                  'fecha_colacion': 'Fecha Colación'})
        db['Registro'] = f'Libro: {str(db.Libro.iloc[0])}, Folio: {(db.Folio.iloc[0])}, Orden: {db.Orden.iloc[0]}'
        db = db.drop(['Nro Solicitud','Libro','Folio','Orden'], axis=1)

        db = db[['Nro Resolución', 'Fecha Resolución', 'Res UNTREF','Res RME', 'Res CONEAU', 'Registro', 'Egreso',
                 'Emisión Diploma','Nro SIDCER', 'Nro Diploma', 'Finalización SIDCER', 'Fecha Colación']]

        db = db.T
        db.reset_index(inplace=True)
        db.columns = ['Dato','Valor']

        #print({i: i for i in datos_solicitud.columns})

    return [
        db.to_dict('records'),
        [{"name": i, "id": i} for i in db.columns],
        tit
        ]

@app.callback(
    [
        Output('tabla-datos-sol-documentacion', 'data'),
        Output('tabla-datos-sol-documentacion', 'columns'),
        Output('solicitud-elegida-documentacion', 'children'),
    ],
    [
        Input('tabla-solicitudes', 'derived_virtual_selected_rows'),
        Input('nro-solicitud-elegida', 'children'),
    ],
)
def solicitud_seleccionada_documentacion(fila,sol_selected):
    db = pd.DataFrame()
    tit = ''

    if type(sol_selected) == str:
        if sol_selected == 'Seleccione una solicitud':
            sol_selected = ''
        else:
            sol_selected = int(sol_selected.strip('Solicitud Nro: '))
            tit = 'Documentación presentada:'

    if len(str(sol_selected)) > 0:
        db = consulta.get_datos_documentacion(solicitud=sol_selected)
        db = db.drop(['grupo'], axis=1)
        db = db.rename(columns = {'grupo': 'Grupo', 'solicitud_alumno': 'Solicitud del Alumno',
                                  'libre_deuda': 'Libre Deuda', 'tesis_cd': 'CD Tesis-TFI',
                                  'titulo_previo': 'Título Previo', 'documento': 'Documento Identidad',
                                  'car': 'C.A.R.', 'nota_dir': 'Nota Director', 'acta_final': 'Acta Final',
                                  'actas_totales': 'Totalidad de Actas'})

        db = db.T
        db.reset_index(inplace=True)
        db.columns = ['Documentación','Presentada']

        #print({i: i for i in db.columns})

    return [
        db.to_dict('records'),
        [{"name": i, "id": i} for i in db.columns],
        tit
        ]



################################ CALL BACKS ##################################
################################# APP LOOP ###################################
if __name__ == '__main__':
    app.run_server(debug=True)
