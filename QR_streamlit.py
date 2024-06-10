import streamlit as st
import qrcode
from PIL import Image
import validators
import re
import io

def load_css():
    with open("static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

load_css()        

def generar_qr(url, nombre_archivo=None, redimension_logo=0.8, logo_file=None, espacio_entre_logo_y_qr=0, margen_arriba=25, margen_abajo=25, margen_izquierda=20, margen_derecha=20, tamanio_modulo=10):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=tamanio_modulo,
        border=4,
    )
    qr.add_data(url)
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
            
            if nombre_archivo:
                nueva_imagen.save(nombre_archivo)
        except Exception as e:
            st.warning(f"Error al procesar el logo: {e}. Generando el código QR sin el logo.")
            if nombre_archivo:
                imagen_qr.save(nombre_archivo)
            imagen_mostrar = imagen_qr
        else:
            imagen_mostrar = nueva_imagen
    else:
        if nombre_archivo:
            imagen_qr.save(nombre_archivo)
        imagen_mostrar = imagen_qr
    
    if nombre_archivo:
        st.success(f"El código QR ha sido generado y guardado como '{nombre_archivo}'.")
    
    # Convertir la imagen a bytes para mostrarla en Streamlit
    imagen_bytes = io.BytesIO()
    imagen_mostrar.save(imagen_bytes, format='PNG')
    return imagen_bytes.getvalue()


def generar_qr_desde_interfaz():
    logo_file = st.sidebar.file_uploader("Seleccionar logo (opcional)", type=["png", "jpg", "jpeg"])
    redimension_logo = st.sidebar.slider("Redimensión del Logo", min_value=0.1, max_value=1.0, step=0.05, value=0.8)
    espacio_entre_logo_y_qr = st.sidebar.slider("Espacio entre logo y QR", min_value=-150, max_value=20, step=1, value=-20)

    st.header("QR para Página Web")
    url = st.text_input("URL", "https://magneticasg.com/nuestro-equipo/")
    nombre_archivo_qr = st.text_input("Nombre del archivo", "qr_code.png")
    
    if st.button("Generar"):
        if not nombre_archivo_qr:
            st.error("Por favor, ingresa un nombre de archivo para el código QR.")
            return
        
        if not validators.url(url):
            st.error("Por favor, ingresa una URL válida.")
            return
        
        imagen_bytes = generar_qr(url, nombre_archivo_qr + ".png", redimension_logo, logo_file, espacio_entre_logo_y_qr, tamanio_modulo=20)
        st.image(imagen_bytes, caption="Código QR generado")
    
    if url and validators.url(url):
        # Mostrar previsualización en tiempo real
        imagen_bytes = generar_qr(url, None, redimension_logo, logo_file, espacio_entre_logo_y_qr, tamanio_modulo=20)
        st.sidebar.image(imagen_bytes, caption="Previsualización del Código QR")

def generar_vcard_qr_desde_interfaz():
    logo_file = st.sidebar.file_uploader("Seleccionar logo (opcional)", type=["png", "jpg", "jpeg"])
    redimension_logo = st.sidebar.slider("Redimensión del Logo", min_value=0.1, max_value=1.0, step=0.05, value=0.8)
    espacio_entre_logo_y_qr = st.sidebar.slider("Espacio entre logo y QR", min_value=-150, max_value=20, step=1, value=-20)

    st.header("QR Contacto y vCard")
    col1, col2 = st.columns(2)

    with col1:
        nombres = st.text_input("Nombres", "")
        celular = st.text_input("Celular", "")
        empresa = st.text_input("Empresa", "")
        correo = st.text_input("Correo", "")

    with col2:
        apellidos = st.text_input("Apellidos", "")
        direccion = st.text_input("Dirección", "")
        ciudad = st.text_input("Ciudad", "")
        pagina_web = st.text_input("Página Web", "https://")

    nombre_archivo_qr = st.text_input("Nombre del archivo", "vcard_qr_code")

    #if nombres and apellidos and celular:
        # Mostrar previsualización en tiempo real
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

    imagen_bytes = generar_qr(vcard, None, redimension_logo, logo_file, espacio_entre_logo_y_qr)
    st.sidebar.image(imagen_bytes, caption="Previsualización del Código QR")

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

        nombre_archivo_qr_vcard = nombre_archivo_qr + ".png"  
        imagen_bytes = generar_qr(vcard, nombre_archivo_qr_vcard, redimension_logo, logo_file, espacio_entre_logo_y_qr)
        st.image(imagen_bytes, caption="Código QR generado")

        # Guardar vCard
        ruta_guardado_vcard = nombre_archivo_qr + ".vcf"
        with open(ruta_guardado_vcard, "w", encoding="utf-8") as vcard_file:
            vcard_file.write(vcard)
        st.success(f"La vCard ha sido generada y guardada como '{ruta_guardado_vcard}'.")



def main():
    st.sidebar.title("Generador de Códigos QR")
    option = st.sidebar.radio("Selecciona una opción", ["Generar QR para URL", "Generar QR de Contacto y vCard"])

    if option == "Generar QR para URL":
        generar_qr_desde_interfaz()
    elif option == "Generar QR de Contacto y vCard":
        generar_vcard_qr_desde_interfaz()

if __name__ == "__main__":
    main()
