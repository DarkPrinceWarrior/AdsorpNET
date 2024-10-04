import streamlit


def contact_action():
    streamlit.title("Контакты по проекту")
    text = "### <div class='div_text'>" \
           "Лаборатория сорбционных процессов <br>" \
           "<br>Федеральное государственное бюджетное учреждение науки Институт физической химии и электрохимии им. " \
           "А.Н.Фрумкина Российской академии наук ИФХЭ РАН <br><br>" \
           "Email: knyazeva.mk@phyche.ac.ru " \
           "<br> Web: http://sorptionlab.ru - M.M.Dubinin Laboratory of sorption processes " \
           "https://adsorbtech.ru / - Engineering & Technical Center <br> <br> </div>"
    streamlit.markdown(text, unsafe_allow_html=True)


def team_action(team_image,achievments_image):
    streamlit.title("Лаборатория сорбционных процессов ИФХЭ РАН")
    text1 = "### <div class='div_text'>" \
           "Команда высококвалифицированных и " \
           "опытных специалистов — лидеров отрасли" \
           " в области адсорбционных технологий в России и СНГ<br><br> </div>"
    streamlit.markdown(text1, unsafe_allow_html=True)
    streamlit.image(team_image, width=800)
    streamlit.title("Научно-технические разработки")
    text2 = "### <div class='div_text'>" \
           "Помимо проведения исследований центр «Адсорбционные Технологии» " \
            "обладает потенциалом для создания образцов абсолютно " \
            "новых продуктов для различных сфер применения, включая все " \
            "этапы жизненного цикла изделия<br><br> </div>"
    streamlit.markdown(text2, unsafe_allow_html=True)
    streamlit.image(achievments_image, width=800)