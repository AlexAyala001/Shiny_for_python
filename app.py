from pathlib import Path
import os
import plotly.express as px
import pandas as pd
import seaborn as sns
import faicons as fa
from shiny import reactive
from shiny.express import input, render, ui
import shinyswatch
from shinywidgets import render_widget


sns.set_theme(style="white")
df = pd.read_csv(Path(__file__).parent / "ofertas.csv", dtype={'Tipo_oferta':str})
df['info_day'] = pd.to_datetime(df['info_day'])
df['Tipo_oferta']=df['Tipo_oferta'].astype(str)

Tipo_oferta= ['total','sin_oferta','con_oferta','fiserv']

ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "users": fa.icon_svg("users"),
    "address-card": fa.icon_svg("address-card"),
    "ban": fa.icon_svg("ban"),
    "ellipsis": fa.icon_svg("ellipsis")
}

ui.page_opts(title="Reporte ofertas de credito", fillable=True, theme=shinyswatch.theme.cerulean)
#theme.cerulean()

def count_ofertas(df,columna):
    return df[columna][0]



with ui.sidebar():
    ui.input_date('fecha','Fecha de consulta', value="2024-08-20")
    ui.input_radio_buttons("TipoOferta", "Filtra por tipo de oferta", Tipo_oferta,selected='total')


@reactive.Calc
    
def filtered_df() -> pd.DataFrame:
    filt_df = df.loc[df["info_day"] == f"{input.fecha()}"].reset_index()
    filt_df1 = filt_df.loc[filt_df["Tipo_oferta"] == f"{input.TipoOferta()}"].reset_index()
    return filt_df1

def filtradodf() -> pd.DataFrame:
    filtrado_df = df.loc[df["Tipo_oferta"] == f"{input.TipoOferta()}"].reset_index()
    return filtrado_df



with ui.layout_column_wrap(fill=False):
    with ui.value_box(showcase=ICONS["users"], theme='gradient-blue-indigo'):
        "Total cuentas"

        @render.text
        def totalcuetas_count():
            valor_numerico = count_ofertas(filtered_df(),'Total_cuentas')
            cadena_formateada = "{:,.0f}".format(valor_numerico)
            return cadena_formateada
    
    with ui.value_box(showcase=ICONS["address-card"],theme='gradient-blue-indigo'):
        "Adopcion digital completa"

        @render.text
        def adopcion_count():
            valor_numerico = count_ofertas(filtered_df(),'Adopcion_completa')
            cadena_formateada = "{:,.0f}".format(valor_numerico)
            return cadena_formateada

    with ui.value_box(showcase=ICONS["user"], theme='gradient-blue-indigo'):
        "Solo facescan"

        @render.text
        def solofacescan_count():
            valor_numerico =count_ofertas(filtered_df(),'Solo_facescan')
            cadena_formateada = "{:,.0f}".format(valor_numerico)
            return cadena_formateada
    
    with ui.value_box(showcase=ICONS["ban"],theme='gradient-blue-indigo'):
        "Sin adopcion completa"

        @render.text
        def soloine_count():
            valor_numerico= count_ofertas(filtered_df(),'Sin_adopcion')
            cadena_formateada = "{:,.0f}".format(valor_numerico)
            return cadena_formateada


with ui.navset_card_underline(title="Resumen"):
    with ui.nav_panel("Historico totales"):
        @render_widget
        def hist():
            df_plot= filtradodf()
            df_plot = df_plot[-15:].reset_index()
            fig = px.line(df_plot, x="info_day", y="Total_cuentas",markers=True, title=f"Historico cuentas {input.TipoOferta()}") 
            fig.update_traces(line=dict(color="royalblue"))
            fig.update_layout(
            plot_bgcolor='rgba(255, 255, 255, 0)',  # Color de fondo transparente
            paper_bgcolor='rgb(255, 255, 255)',     # Color del papel (fondo) blanco
            xaxis=dict(showgrid=False),             # Ocultar cuadrícula en el eje x
            yaxis=dict(showgrid=False)              # Ocultar cuadrícula en el eje y
            )
            return fig
    
    with ui.nav_panel("Comparativo"):
        @render_widget
        def barplot():
            df_plot= filtradodf()
            df_plot = df_plot[-5:].reset_index()
            df_bar = df_plot[['Total_cuentas','Solo_facescan','Sin_adopcion','Adopcion_completa','info_day']]
            df_long = pd.melt(df_bar, id_vars='info_day', var_name='variable', value_name='valor')

            # gráfica de barras agrupadas
            fig = px.bar(df_long, x='info_day', y='valor', color='variable', barmode='group', 
                        title=f'Comparativo {input.TipoOferta()} por info_day',
                        color_discrete_sequence=['navy','royalblue','cornflowerblue','lightskyblue', 'lightskyblue', 'mediumturquoise'])
# peleturquoise
# mediumturquoise

            fig.update_layout(
            plot_bgcolor='rgba(255, 255, 255, 0)',  # Color de fondo transparente
            paper_bgcolor='rgb(255, 255, 255)',     # Color del papel (fondo) blanco
            xaxis=dict(showgrid=False),             # Ocultar cuadrícula en el eje x
            yaxis=dict(showgrid=False)              # Ocultar cuadrícula en el eje y
            )
            return fig

    with ui.nav_panel("Tabla historico"):
        with ui.popover(title="Acciones", placement="top"):
            ICONS["ellipsis"]
            @render.download(label="Descargar csv")
            def download1():
                path = os.path.join(os.path.dirname(__file__), "ofertas.csv")
                return path
        @render.data_frame
        def table():
            display= df.copy()
            display['info_day'] = pd.to_datetime(display['info_day'])
            display['Fecha_conuslta'] = display['info_day'].dt.strftime('%Y%m%d')
            display_df= display[['Total_cuentas', 'Adopcion_completa','Solo_facescan','Sin_adopcion','Tipo_oferta', 'Fecha_conuslta']]
            return render.DataGrid(display_df,filters=True)