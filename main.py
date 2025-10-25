from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from datetime import datetime
import pyttsx3
import speech_recognition as sr
from reportlab.pdfgen import canvas
import os

# -------------------------------
# BASE DE DONNÉES SIMULÉE
# -------------------------------
patients = []

# -------------------------------
# LISTE DES MÉDECINS ET SERVICES
# -------------------------------
medecins = ["Dr. Zongo", "Dr. Traoré", "Dr. Ouédraogo"]
services = [
    "Médecine interne", "Pédiatrie", "Chirurgie", "Cardiologie", "Gynécologie",
    "Neurologie", "Dermatologie", "Oto-rhino", "Ophtalmologie", "Urgences",
    "Radiologie", "Anesthésie", "Gastro-entérologie", "Hématologie",
    "Endocrinologie", "Néphrologie", "Rhumatologie", "Psychiatrie",
    "Pneumologie", "Urologie"
]

# -------------------------------
# RECONNAISSANCE ET SYNTHÈSE VOCALE
# -------------------------------
def speech_to_text():
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎙️ Parlez maintenant...")
            audio = recognizer.listen(source)
        text = recognizer.recognize_google(audio, language="fr-FR")
        print(f"Texte reconnu : {text}")
        return text
    except Exception as e:
        print(f"Erreur reconnaissance vocale : {e}")
        return ""

def read_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# -------------------------------
# GÉNÉRATION DU PDF
# -------------------------------
def generate_pdf(patient):
    dossier = "dossiers_pdf"
    os.makedirs(dossier, exist_ok=True)
    filename = os.path.join(dossier, f"patient_{patient['Identifiant']}.pdf")

    c = canvas.Canvas(filename)
    c.setFont("Helvetica", 12)
    c.drawString(50, 800, f"Dossier du patient : {patient['Nom']} ({patient['Identifiant']})")
    c.drawString(50, 780, f"Médecin responsable : {patient['Médecin']}")
    c.drawString(50, 760, f"Date d’ajout : {patient['Date ajout']}")
    y = 740

    for champ, value in patient.items():
        if champ not in ["Médecin", "Identifiant", "Nom", "Date ajout"]:
            for line in value.split("\n"):
                c.drawString(50, y, f"{champ} : {line}")
                y -= 20
                if y < 50:
                    c.showPage()
                    y = 800

    c.save()
    print(f"✅ PDF généré : {filename}")

# -------------------------------
# PAGE DE CONNEXION
# -------------------------------
class LoginPage(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.add_widget(Label(text="Identifiant du médecin :", font_size=20))
        self.input_medecin = TextInput(multiline=False)
        self.add_widget(self.input_medecin)

        btn_login = Button(text="Se connecter", size_hint=(1, 0.2))
        btn_login.bind(on_press=self.login)
        self.add_widget(btn_login)

        self.message = Label(text="", color=(1, 0, 0, 1))
        self.add_widget(self.message)

    def login(self, instance):
        identifiant = self.input_medecin.text.strip()
        if identifiant in medecins:
            self.clear_widgets()
            self.add_widget(ServicePage(selected_medecin=identifiant))
        else:
            self.message.text = "Médecin non reconnu !"

# -------------------------------
# PAGE DE CHOIX DU SERVICE
# -------------------------------
class ServicePage(BoxLayout):
    def __init__(self, selected_medecin, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.selected_medecin = selected_medecin

        self.add_widget(Label(text=f"Bienvenue {selected_medecin} !", font_size=18))
        self.spinner = Spinner(text="Choisissez un service", values=services)
        self.add_widget(self.spinner)

        btn_open = Button(text="Entrer dans le service")
        btn_open.bind(on_press=self.open_service)
        self.add_widget(btn_open)

    def open_service(self, instance):
        if self.spinner.text != "Choisissez un service":
            self.clear_widgets()
            self.add_widget(ServicePortal(self.spinner.text, self.selected_medecin))

# -------------------------------
# PORTAIL DU SERVICE
# -------------------------------
class ServicePortal(BoxLayout):
    def __init__(self, service_name, medecin, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.service_name = service_name
        self.medecin = medecin

        self.add_widget(Label(text=f"Bienvenue dans le service {service_name} !", font_size=18))

        btn_add = Button(text="➕ Ajouter un patient")
        btn_add.bind(on_press=self.add_patient)
        self.add_widget(btn_add)

        btn_update = Button(text="📝 Mettre à jour un dossier")
        btn_update.bind(on_press=self.update_patient)
        self.add_widget(btn_update)

        btn_search = Button(text="🔍 Rechercher un patient")
        btn_search.bind(on_press=self.search_patient)
        self.add_widget(btn_search)

        btn_stats = Button(text="📊 Statistiques")
        btn_stats.bind(on_press=self.stats)
        self.add_widget(btn_stats)

    def add_patient(self, instance):
        self.clear_widgets()
        self.add_widget(AddPatientForm(self.medecin))

    def update_patient(self, instance):
        self.clear_widgets()
        self.add_widget(UpdatePatientForm())

    def search_patient(self, instance):
        self.clear_widgets()
        self.add_widget(SearchPatientForm())

    def stats(self, instance):
        self.clear_widgets()
        self.add_widget(Label(text=f"Nombre total de patients : {len(patients)}", font_size=18))

# -------------------------------
# AJOUT D’UN PATIENT
# -------------------------------
class AddPatientForm(BoxLayout):
    def __init__(self, medecin, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.medecin = medecin
        self.inputs = {}

        champs = [
            "Nom", "Identifiant", "Motif de consultation",
            "Histoire de la maladie", "Examen général", "Bilan paraclinique",
            "Diagnostic", "Traitement"
        ]

        scroll = ScrollView(size_hint=(1, 0.85))
        inner = BoxLayout(orientation='vertical', size_hint_y=None)
        inner.bind(minimum_height=inner.setter('height'))

        for champ in champs:
            inner.add_widget(Label(text=champ))
            self.inputs[champ] = TextInput(multiline=True, size_hint_y=None, height=100)
            inner.add_widget(self.inputs[champ])
            btn_voice = Button(text=f"🎤 Dictée vocale ({champ})", size_hint_y=None, height=40)
            btn_voice.bind(on_press=lambda inst, c=champ: self.voice_input(c))
            inner.add_widget(btn_voice)

        scroll.add_widget(inner)
        self.add_widget(scroll)

        btn_save = Button(text="💾 Enregistrer", size_hint=(1, 0.15))
        btn_save.bind(on_press=self.save_patient)
        self.add_widget(btn_save)

        self.message = Label(text="")
        self.add_widget(self.message)

    def voice_input(self, champ):
        texte = speech_to_text()
        if texte:
            self.inputs[champ].text = texte

    def save_patient(self, instance):
        patient = {champ: self.inputs[champ].text for champ in self.inputs}
        patient["Médecin"] = self.medecin
        patient["Date ajout"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        patients.append(patient)
        generate_pdf(patient)
        self.message.text = f"✅ Patient {patient['Nom']} ajouté avec succès"
        read_text(self.message.text)

# -------------------------------
# MISE À JOUR DU DOSSIER
# -------------------------------
class UpdatePatientForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(Label(text="Identifiant du patient :"))
        self.input_id = TextInput(multiline=False)
        self.add_widget(self.input_id)
        btn_find = Button(text="Rechercher")
        btn_find.bind(on_press=self.find_patient)
        self.add_widget(btn_find)
        self.result_area = BoxLayout(orientation='vertical')
        self.add_widget(self.result_area)

    def find_patient(self, instance):
        pid = self.input_id.text.strip()
        for p in patients:
            if p["Identifiant"] == pid:
                self.result_area.clear_widgets()
                self.inputs = {}
                for champ in ["Motif de consultation", "Bilan paraclinique", "Traitement"]:
                    self.result_area.add_widget(Label(text=f"Modifier {champ}:"))
                    self.inputs[champ] = TextInput(text=p.get(champ, ""))
                    self.result_area.add_widget(self.inputs[champ])
                btn_save = Button(text="💾 Sauvegarder modifications")
                btn_save.bind(on_press=lambda inst, pat=p: self.save_update(pat))
                self.result_area.add_widget(btn_save)
                return
        self.result_area.add_widget(Label(text="⚠️ Patient introuvable"))

    def save_update(self, patient):
        for champ in self.inputs:
            patient[champ] = self.inputs[champ].text
        generate_pdf(patient)
        read_text(f"Dossier de {patient['Nom']} mis à jour.")

# -------------------------------
# RECHERCHE DE PATIENT
# -------------------------------
class SearchPatientForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(Label(text="Nom ou Identifiant :"))
        self.input_search = TextInput(multiline=False)
        self.add_widget(self.input_search)
        btn_search = Button(text="Rechercher")
        btn_search.bind(on_press=self.search)
        self.add_widget(btn_search)
        self.result_area = ScrollView(size_hint=(1, 0.7))
        self.add_widget(self.result_area)

    def search(self, instance):
        query = self.input_search.text.lower()
        layout = BoxLayout(orientation='vertical', size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        for p in patients:
            if query in p["Nom"].lower() or query in p["Identifiant"].lower():
                layout.add_widget(Label(text="\n".join(f"{k}: {v}" for k, v in p.items()), size_hint_y=None, height=150))
        self.result_area.clear_widgets()
        self.result_area.add_widget(layout)

# -------------------------------
# APPLICATION PRINCIPALE
# -------------------------------
class ZAIInnovApp(App):
    def build(self):
        return LoginPage()

if __name__ == "__main__":
    ZAIInnovApp().run()
