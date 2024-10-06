import streamlit as st
import base64


def contact_action():
    st.title("Контакты по проекту")
    text = "### <div class='div_text'>" \
           "Лаборатория сорбционных процессов <br>" \
           "<br>Федеральное государственное бюджетное учреждение науки Институт физической химии и электрохимии им. " \
           "А.Н.Фрумкина Российской академии наук ИФХЭ РАН <br><br>" \
           "Email: knyazeva.mk@phyche.ac.ru " \
           "<br> Web: http://sorptionlab.ru - M.M.Dubinin Laboratory of sorption processes " \
           "https://adsorbtech.ru / - Engineering & Technical Center <br> <br> </div>"
    st.markdown(text, unsafe_allow_html=True)


@st.cache_data
def get_img_as_base64(file):
    """
    Читает изображение и возвращает его в формате base64.
    """
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def team_action(team_image):
    """
    Отображает страницу "О нас" с заголовком, текстом и изображением в рамке.
    """
    # Основной заголовок
    st.markdown("<div class='main-title'>Лаборатория сорбционных процессов ИФХЭ РАН</div>", unsafe_allow_html=True)
    
    # Основной текст
    text1 = """
    <div class='div_text'>
        Представляем вашему вниманию первый в России программный 
        инструмент для реверс инжиниринга адсорбционных материалов.<br><br>
    </div>
    """
    st.markdown(text1, unsafe_allow_html=True)
    
    # Изображение в рамке
    image_base64 = get_img_as_base64(team_image)
    image_html = f"""
    <div class='image-frame'>
        <img src='data:image/jpeg;base64,{image_base64}' width='800'/>
    </div>
    """
    st.markdown(image_html, unsafe_allow_html=True)
    
    # Секционный заголовок
    st.markdown("<div class='section-title'>Научно-технические разработки</div>", unsafe_allow_html=True)
    
    # Второй текст
    text2 = """
    <div class='div_text'>
        Помимо функционала по предсказанию синтеза адсорбционных материалов, вы найдете:<br> 
        1) chatMOF <br>
        2) Рекомендательную систему по прецизионному подбору адсорбентов <br><br>
    </div>
    """
    st.markdown(text2, unsafe_allow_html=True)