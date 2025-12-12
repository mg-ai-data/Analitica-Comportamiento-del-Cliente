from google.colab import files
uploaded = files.upload()

2) Pegar en otra celda vacía.

!ls /content

3) Pegar en otra celda vacía.

# ======================================
# 1) Instalar dependencias
# ======================================
!pip install gradio pandas

# ======================================
# 2) Importar módulos
# ======================================
import pandas as pd
import gradio as gr

# ======================================
# 3) Cargar CSV (arreglando comillas)
# ======================================
# Le decimos a pandas que elimine las comillas externas
df = pd.read_csv(
    "clientes.csv",
    quotechar='"',
    skipinitialspace=True,
    engine="python"
)

# Si las líneas están completas dentro de una única columna, las separamos:
if len(df.columns) == 1:
    df = df.iloc[:,0].str.replace('"','').str.split(",", expand=True)
    df.columns = ["cliente_id","pagina_visitada","producto_visto","tiempo_sesion_segundos","compro"]
    df["tiempo_sesion_segundos"] = df["tiempo_sesion_segundos"].astype(int)


# ======================================
# 4) Función de respuestas
# ======================================
def responder(pregunta):
    try:
        pregunta = pregunta.lower()

        # ---- Tasa de conversión ----
        if "convers" in pregunta:
            conversion = (df["compro"] == "si").mean() * 100
            return f"La tasa de conversión actual es {conversion:.2f}%."

        # ---- Página con mayor conversión ----
        if "página" in pregunta or "pagina" in pregunta:
            conv = df.groupby("pagina_visitada")["compro"].apply(lambda x: (x=="si").mean()*100)
            mejor = conv.idxmax()
            return f"La página con mejor conversión es '{mejor}', con {conv.max():.2f}%."

        # ---- Producto más visto ----
        if "producto" in pregunta and ("más" in pregunta or "mas" in pregunta):
            p = df["producto_visto"].value_counts().idxmax()
            return f"El producto más visto es '{p}'."

        # ---- Tiempo promedio de sesión ----
        if "tiempo" in pregunta or "sesión" in pregunta or "sesion" in pregunta:
            t = df["tiempo_sesion_segundos"].mean()
            return f"El tiempo promedio de sesión es {t:.2f} segundos."

        # ---- Por si no matchea nada ----
        return "No encontré información para esa consulta."

    except Exception as e:
        return f"[ERROR] → {e}"

# ======================================
# 5) Interfaz con Gradio
# ======================================
with gr.Blocks() as app:
    gr.Markdown("# 📊 Analítica de Comportamiento del Cliente")
    gr.Markdown("Analiza comportamiento, conversiones y productos vistos.")

    inp = gr.Textbox(label="Tu consulta", placeholder="Ejemplo: tasa de conversión")
    out = gr.Textbox(label="Respuesta")

    btn = gr.Button("Consultar")
    btn.click(fn=responder, inputs=inp, outputs=out)

app.launch(share=True)
