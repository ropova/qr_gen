import streamlit as st
import qrcode
from PIL import Image
import validators
import re
import io
import zipfile

def load_css():
    with open("static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

load_css()

def generar_qr(data, redimension_logo=0.8, logo_file=None, espacio_entre_logo_y_qr=0, margen_arriba=0, margen_abajo=10, margen_izquierda=10, margen_derecha=10, tamanio_modulo=10):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=tamanio_modulo,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)
    imagen_qr = qr.make_image(fill_color="black", back_color="white")
    
    if logo_file:
        try:
            logo = Image.open(logo_file).convert("RGBA")
            ancho_qr, alto_qr = imagen_qr.size
            ancho_logo_redimensionado = int(ancho_qr * redimension_logo)
            proporcion_logo = ancho_logo_redimensionado / logo.size[0]
            alto_logo_redimensionado = int(logo.size[1] * proporcion_logo)
            logo_redimensionado = logo.resize((ancho_logo_redimensionado, alto_logo_redimensionado), Image.LANCZOS)

            altura_total = alto_qr + alto_logo_redimensionado + espacio_entre_logo_y_qr + margen_arriba + margen_abajo
            nueva_imagen = Image.new("RGB", (ancho_qr + margen_izquierda + margen_derecha, altura_total), "white")

            posicion_qr = (margen_izquierda, alto_logo_redimensionado + espacio_entre_logo_y_qr + margen_arriba)
            nueva_imagen.paste(imagen_qr, posicion_qr)

            posicion_logo = ((nueva_imagen.size[0] - ancho_logo_redimensionado) // 2, margen_arriba)
            nueva_imagen.paste(logo_redimensionado, posicion_logo, logo_redimensionado)
            
        except Exception as e:
            st.warning(f"Error al procesar el logo: {e}. Generando el código QR sin el logo.")
            imagen_mostrar = imagen_qr
        else:
            imagen_mostrar = nueva_imagen
    else:
        imagen_mostrar = imagen_qr
    
    # Convertir la imagen a bytes para mostrarla en Streamlit
    imagen_bytes = io.BytesIO()
    imagen_mostrar.save(imagen_bytes, format='PNG')
    return imagen_bytes.getvalue()


def generar_qr_desde_interfaz():

    # Inicializar variables con valores predeterminados
    redimension_logo = None
    espacio_entre_logo_y_qr = None

    # Subir archivo de logo
    logo_file = st.sidebar.file_uploader("Seleccionar logo (opcional)", type=["png", "jpg", "jpeg"])

    # Verificar si se ha cargado una imagen
    if logo_file is not None:
        # Mostrar sliders solo si se ha cargado una imagen de logo
        espacio_entre_logo_y_qr = st.sidebar.slider("Espacio entre logo y QR", min_value=-150, max_value=20, step=1, value=-20)
        redimension_logo = st.sidebar.slider("Redimensión del Logo", min_value=0.1, max_value=1.0, step=0.05, value=0.8)

    if logo_file is None:
        espacio_entre_logo_y_qr = 0
        redimension_logo = 0

    # Código para centrar el subtítulo
    st.sidebar.markdown("<h2 style='text-align: center;'>Previsualización QR</h2>", unsafe_allow_html=True) 
    

    st.header("QR para Página Web")
    url = st.text_input("\\* URL", "https://magneticasg.com/nuestro-equipo/")
    nombre_archivo_qr = st.text_input("\\* Nombre del archivo", "qr_code.png")

    st.markdown("<span style='color: red;'>* Campos obligatorios</span>", unsafe_allow_html=True)  
    
    if st.button("Generar"):
        if not nombre_archivo_qr:
            st.error("Por favor, ingresa un nombre de archivo para el código QR.")
            return
        
        if not validators.url(url):
            st.error("Por favor, ingresa una URL válida.")
            return
        
        imagen_bytes = generar_qr(url, redimension_logo, logo_file, espacio_entre_logo_y_qr + 18, tamanio_modulo=15)
        st.image(imagen_bytes)

        st.download_button(
            label="Descargar QR",
            data=imagen_bytes,
            file_name=nombre_archivo_qr + ".png",
            mime="image/png"
        )
    
    if nombre_archivo_qr and url:
        # Mostrar previsualización en tiempo real
        imagen_bytes = generar_qr(url, redimension_logo, logo_file, espacio_entre_logo_y_qr, tamanio_modulo=20)
        st.sidebar.image(imagen_bytes)
    else:
        st.sidebar.markdown(
            """
            <div style="text-align: center; font-size: 12px; color: red">
                <strong>* Para previsualizar, completa los campos obligatorios</strong>
            </div>
            """,
            unsafe_allow_html=True
        )     

def generar_vcard_qr_desde_interfaz():

    # Inicializar variables con valores predeterminados
    redimension_logo = None
    espacio_entre_logo_y_qr = None

    # Subir archivo de logo
    logo_file = st.sidebar.file_uploader("Seleccionar logo (opcional)", type=["png", "jpg", "jpeg"])

    # Verificar si se ha cargado una imagen
    if logo_file is not None:
        # Mostrar sliders solo si se ha cargado una imagen de logo
        espacio_entre_logo_y_qr = st.sidebar.slider("Espacio entre logo y QR", min_value=-150, max_value=20, step=1, value=-20)
        redimension_logo = st.sidebar.slider("Redimensión del Logo", min_value=0.1, max_value=1.0, step=0.05, value=0.8)

    if logo_file is None:
        espacio_entre_logo_y_qr = 0
        redimension_logo = 0

    # Código para centrar el subtítulo
    st.sidebar.markdown("<h2 style='text-align: center;'>Previsualización QR</h2>", unsafe_allow_html=True)       

    st.header("QR Contacto y vCard")
    col1, col2 = st.columns(2)

    with col1:
        nombres = st.text_input("\\* Nombres", "")
        celular = st.text_input("\\* Celular", "")
        empresa = st.text_input("Empresa", "")
        correo = st.text_input("Correo", "")

    with col2:
        apellidos = st.text_input("\\* Apellidos", "")
        direccion = st.text_input("Dirección", "")
        ciudad = st.text_input("Ciudad", "")
        pagina_web = st.text_input("Página Web", "https://")

    st.markdown("<span style='color: red;'>* Campos obligatorios</span>", unsafe_allow_html=True)        

    nombre_archivo_qr = st.text_input("Nombre del archivo", "vcard_qr_code")

    vcard = (
        f"BEGIN:VCARD\n"
        f"VERSION:3.0\n"
        f"N;CHARSET=UTF-8:{apellidos};{nombres};;;\n"
        f"FN;CHARSET=UTF-8:{nombres} {apellidos}\n"
        f"ORG;CHARSET=UTF-8:{empresa}\n"
        f"TEL;TYPE=CELL:{celular}\n"
        f"EMAIL;CHARSET=UTF-8:{correo}\n"
        f"ADR;TYPE=HOME;CHARSET=UTF-8:{direccion}, {ciudad};;;\n"
        f"URL;CHARSET=UTF-8:{pagina_web}\n"
        f"END:VCARD"
    )

    if nombres and apellidos and celular:
        imagen_bytes = generar_qr(vcard, redimension_logo, logo_file, espacio_entre_logo_y_qr)
        st.sidebar.image(imagen_bytes)
    else:
        st.sidebar.markdown(
            """
            <div style="text-align: center; font-size: 12px; color: red">
                <strong>* Para previsualizar, completa los campos obligatorios</strong>
            </div>
            """,
            unsafe_allow_html=True
        ) 

    if st.button("Generar"):
        if not (nombres and apellidos and celular):
            st.error("Por favor, completa los campos obligatorios: Nombres, Apellidos, y Celular.")
            return

        if correo and not validators.email(correo):
            st.error("Por favor, ingresa una dirección de correo electrónico válida.")
            return

        if pagina_web and not validators.url(pagina_web):
            st.error("Por favor, ingresa una URL válida para la página web.")
            return

        if celular and not re.match("^[0-9]+$", celular):
            st.error("Por favor, ingresa solo números en el campo de número de teléfono.")
            return

        vcard = (
            f"BEGIN:VCARD\n"
            f"VERSION:3.0\n"
            f"N;CHARSET=UTF-8:{apellidos};{nombres};;;\n"
            f"FN;CHARSET=UTF-8:{nombres} {apellidos}\n"
            f"ORG;CHARSET=UTF-8:{empresa}\n"
            f"TEL;TYPE=CELL:{celular}\n"
            f"EMAIL;CHARSET=UTF-8:{correo}\n"
            f"ADR;TYPE=HOME;CHARSET=UTF-8:{direccion}, {ciudad};;;\n"
            f"URL;CHARSET=UTF-8:{pagina_web}\n"
            f"END:VCARD"
        )

        imagen_bytes = generar_qr(vcard, redimension_logo, logo_file, espacio_entre_logo_y_qr + 18, tamanio_modulo=8)
        st.image(imagen_bytes)        

        # Guardar vCard como archivo .vcf
        vcard_bytes = vcard.encode('utf-8')

        # Crear un archivo ZIP en memoria
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zf:
            zf.writestr(nombre_archivo_qr + ".png", imagen_bytes)
            zf.writestr(nombre_archivo_qr + ".vcf", vcard_bytes)
        
        zip_buffer.seek(0)
        
        # Descargar el archivo ZIP
        st.download_button(
            label="Descargar QR y vCard",
            data=zip_buffer,
            file_name=nombre_archivo_qr + ".zip",
            mime="application/zip"
        )

def main():
    st.sidebar.title("Generador de Códigos QR")
    option = st.sidebar.radio("Selecciona una opción", ["Generar QR para URL", "Generar QR de Contacto y vCard"])

    if option == "Generar QR para URL":
        generar_qr_desde_interfaz()
    elif option == "Generar QR de Contacto y vCard":
        generar_vcard_qr_desde_interfaz()

if __name__ == "__main__":
    main()
