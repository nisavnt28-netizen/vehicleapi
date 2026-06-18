
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

# ==================== DIRECTORIES ====================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILES_DIR = os.path.join(BASE_DIR, "Frontend", "Files")
GRAPHICS_DIR = os.path.join(BASE_DIR, "Frontend", "graphics")

os.makedirs(FILES_DIR, exist_ok=True)
os.makedirs(GRAPHICS_DIR, exist_ok=True)

# ==================== ENV VARS ====================
env_vars = dotenv_values(os.path.join(BASE_DIR, ".env"))
Assistantname = env_vars.get("Assistantname", "Assistant")

# ==================== TEMP VARIABLES ====================
old_chat_message = ""

# ==================== HELPER FUNCTIONS ====================
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how","what","who","where","when","why","which","whose","whom","can you","what's","where's","how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1]+"?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1]+"."
        else:
            new_query += "."
    return new_query.capitalize()

# ==================== MICROPHONE STATUS ====================
def SetMicrophoneStatus(Command):
    file_path = os.path.join(FILES_DIR, 'Mic.data')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    file_path = os.path.join(FILES_DIR, 'Mic.data')
    with open(file_path, 'r', encoding='utf-8') as file:
        Status=file.read()
    return Status
# ==================== ASSISTANT STATUS ====================
def SetAssistantStatus(Status):
    file_path = os.path.join(FILES_DIR, 'Status.data')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    file_path = os.path.join(FILES_DIR, 'Status.data')
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    return Status

def MicButtonInitialed():
    SetMicrophoneStatus("True")

def MicButtonClosed():
    SetMicrophoneStatus("False")       


# ==================== GRAPHICS PATH HELPERS ====================
def GraphicsDirectoryPath(Filename):
    return os.path.join(GRAPHICS_DIR, Filename)

# ==================== TEMP PATH HELPERS ====================
def TempDirectoryPath(Filename):
    return os.path.join(FILES_DIR, Filename)

# ==================== RESPONSE HANDLER ====================
def ShowTextToScreen(Text):
    file_path = os.path.join(FILES_DIR, 'Responses.data')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(Text)

# ---------------- Write text to Responses.data ----------------

class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection,self).__init__()
        self.toggled = True
               # ---------------- Layout ----------------
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10,40,40,100)
        layout.setSpacing(-100)
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)

        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1,1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding))
        text_color = QColor(Qt.blue)
        text_colour_text= QTextCharFormat()
        text_colour_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_colour_text)


                              # ---------------- GIF Label ----------------
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie=QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        max_gif_size_W=480
        max_gif_size_H=170
        movie.setScaledSize(QSize(max_gif_size_W,max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignRight|Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()

        layout.addWidget(self.gif_label)
                              # ---------------- Message Label ----------------
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        layout.setSpacing(-10)       
        font=QFont()
        font.setPointSize(13)
                              # ---------------- Timer ----------------
        self.chat_text_edit.setFont(font)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)  # 5 ms interval
        self.chat_text_edit.viewport().installEventFilter(self)

               # ---------------- Scrollbar Style ----------------
        self.setStyleSheet("""
                                             
            QScrollBar:vertical {
            background: black;
            border:none;
            width: 10px;
            margin: 0px 0px 0px 0px;
            }

                                             
            QScrollBar::handle:vertical {
            background: white;
            min-height: 20px;
            }

                                             
            QScrollBar::add-line:vertical {
            background: black;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
            height: 10px;
            }

                                             
            QScrollBar::sub-line:vertical {
            background: black;
            subcontrol-position: top;
            subcontrol-origin: margin;
            height: 10px;
            }

                                             
            QScrollBar::up-arrow:vertical,QScrollBar::down-arrow:vertical {
            border: none;
            background: none;
            colour: none;
            }

               
            QScrollBar::add-page:vertical,QScrollBar::sub-page:vertical {
            background: none;
            }
        """)

    def loadMessages(self):
                              
        global old_chat_message

        file_path = os.path.join(FILES_DIR, 'Responses.data')
        with open(file_path, 'r', encoding='utf-8') as file:
            messages = file.read()

            if not messages:
                pass

            elif len(messages) <=1:
                pass
                                             
            elif str(old_chat_message) == str(messages):
                pass
                                            
            else:
                                             # Update chat text edit
                self.addMessage(message=messages,color="White")
                old_chat_message = messages

                                             

    def SpeechRecogText(self):
        file_path = os.path.join(FILES_DIR, 'Status.data')
        with open(file_path, 'r', encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)


    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(new_pixmap)


    def toggle_icon(self, event=None):

        if self.toggled:
            self.load_icon(GraphicsDirectoryPath("voice.png"), 60, 60)
            MicButtonInitialed()
                                             
        else:
            self.load_icon(GraphicsDirectoryPath("mic.png"), 60, 60)
            MicButtonClosed()

        self.toggled = not self.toggled

    def addMessage(self, message, color):
                                             # Get text cursor from chat QTextEdit
        cursor = self.chat_text_edit.textCursor() # Set character format (text color)
        format = QTextCharFormat()
        formatm =QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
                                             # Insert message with new line
        cursor.insertText(message + "\n")
                                             # Scroll to bottom after inserting
        self.chat_text_edit.setTextCursor(cursor)
                                             


class InitialScreen(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

        # ---------------- Screen dimensions ----------------
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        # ---------------- Layout ----------------
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        # ---------------- GIF Label ----------------
        gif_label = QLabel()
        movie=QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        gif_label.setMovie(movie)
        max_gif_size_H = int(screen_width / 16 * 9)
        movie.setScaledSize(QSize(screen_width, max_gif_size_H))
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ---------------- Microphone Icon ----------------
        self.icon_label = QLabel()
        mic_path = GraphicsDirectoryPath('Mic_on.png')
        pixmap = QPixmap(mic_path)
        new_pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = False
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        # ---------------- Status Label ----------------
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-bottom: 0;")
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0,0,0,150)

        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")

        # ---------------- Timer ----------------
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)  # 5 ms interval

    # ---------------- Methods ----------------
    def SpeechRecogText(self):
        file_path = os.path.join(FILES_DIR, 'Status.data')
        with open(file_path, "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)

    def load_icon(self, path, width=60, height=60):
            pixmap = QPixmap(path)
            new_pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self,event=None):
        if self.toggled:
            self.load_icon(os.path.join(GRAPHICS_DIR, 'Mic_on.png'), 60, 60)
            MicButtonInitialed()
            
        else:
            self.load_icon(os.path.join(GRAPHICS_DIR, 'Mic_off.png'), 60, 60)
            MicButtonClosed()
            
        self.toggled = not self.toggled                                             

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # ---------------- Screen dimensions ----------------
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        # ---------------- Layout ----------------
        layout = QVBoxLayout()

        # ---------------- Label ----------------
        label = QLabel("")
        layout.addWidget(label)

        # ---------------- ChatSection ----------------
        chat_section = ChatSection()  # pass GraphicsDirPath
        layout.addWidget(chat_section)

        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedWidth(screen_width)
        self.setFixedHeight(screen_height)


class CustomTopBar(QWidget):
    def __init__(self, parent ,stacked_widget):
        super().__init__(parent)

        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        # ---------------- Home Button ----------------
        home_button = QPushButton()
        home_icon = QIcon(GraphicsDirectoryPath("Home.png"))
        home_button.setIcon(home_icon)
        home_button.setText(" Home")
        home_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color: black ")

        # ---------------- Message Button ----------------
        message_button = QPushButton()
        message_icon = QIcon(GraphicsDirectoryPath("Chats.png"))
        message_button.setIcon(message_icon)
        message_button.setText(" Chat")
        message_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color: black")

        # ---------------- Minimize Button ----------------
        minimize_button = QPushButton()
        minimize_icon = QIcon(GraphicsDirectoryPath('Minimize2.png'))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color:white")
        minimize_button.clicked.connect(self.minimizeWindow)

        # ---------------- Maximize / Restore Button ----------------
        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.png'))
        self.restore_icon = QIcon(GraphicsDirectoryPath('Minimize.png'))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        # ---------------- Close Button ----------------
        close_button = QPushButton()
        close_icon = QIcon(GraphicsDirectoryPath('Close.png'))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)

        # ---------------- Horizontal Line ----------------
        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color: black;")

        # ---------------- Title Label ----------------
        title_label = QLabel(f"{str(Assistantname).capitalize()} AI   ")
        title_label.setStyleSheet("color: black; font-size: 18px;; background-color:white")

        # ---------------- Button Actions ----------------
        
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        # ---------------- Add widgets to layout ----------------

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button) 
        layout.addWidget(line_frame)       
        self.draggable =True
        self.offset = None
     

               # ---------------- Paint Event ----------------
    def paintEvent(self, event):
               painter = QPainter(self)
               painter.fillRect(self.rect(), Qt.white)
               super().paintEvent(event)

               # ---------------- Window Controls ----------------
    def minimizeWindow(self):
               
               self.parent().showMinimized()

    def maximizeWindow(self):
               if self.parent().isMaximized():
                              self.parent().showNormal()
                              self.maximize_button.setIcon(self.maximize_icon)
               else:
                              self.parent().showMaximized()
                              self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
               self.parent().close()

               # ---------------- Mouse Dragging ----------------
    def mousePressEvent(self, event):
               if self.draggable:
                      self.offset = event.pos()

    def mouseMoveEvent(self, event):
               if self.draggable and self.offset:
                              new_pos = event.globalPos() - self.offset
                              self.parent().move(new_pos)

               # ---------------- Screen Switching ----------------
    def showMessageScreen(self):
               if self.current_screen is not None:
                    self.current_screen.hide()
               
               message_screen = MessageScreen(self)  # Assuming MessageScreen class exists
               layout = self.parent().layout()
               if layout is not None:
                              layout.addWidget(message_screen)
               self.current_screen = message_screen

    def showInitialScreen(self):
               if self.current_screen is not None :
                          self.current_screen.hide()

               initial_screen=InitialScreen(self)
               layout = self.parent().layout()
               if layout is not None:
                        layout.addWidget(initial_screen)
               self.current_screen = initial_screen    

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        # Frameless window
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        # Stacked Widget
        stacked_widget = QStackedWidget(self)

        # Screens
        initial_screen = InitialScreen()
        message_screen = MessageScreen()

        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)

        # Window geometry
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")

        # Top Bar
        top_bar = CustomTopBar(self ,stacked_widget)
        self.setMenuWidget(top_bar)

        # Central Widget
        self.setCentralWidget(stacked_widget)


# ---------------- GUI Start Function ----------------
def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


# ---------------- Run ----------------
if __name__ == "__main__":
    GraphicalUserInterface()