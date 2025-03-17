"""
Модуль для отображения различных типов сообщений в приложении.
"""

import streamlit as st

def show_success_message(message: str):
    """
    Отображает сообщение об успехе.
    
    Args:
        message (str): Текст сообщения
    """
    st.success(message)

def show_info_message(message: str):
    """
    Отображает информационное сообщение.
    
    Args:
        message (str): Текст сообщения
    """
    st.info(message)

def show_warning_message(message: str):
    """
    Отображает предупреждающее сообщение.
    
    Args:
        message (str): Текст сообщения
    """
    st.warning(message)

def show_error_message(message: str):
    """
    Отображает сообщение об ошибке.
    
    Args:
        message (str): Текст сообщения
    """
    st.error(message) 