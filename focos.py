import sys
import csv
import serial as placa
from PyQt5 import uic, QtWidgets, QtCore


qtCreatorFile = "focos.ui"
Ui_Dialog, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.arduino = None
        self.focos_encendidos = False
        self.valores = []

        # Timer para capturar datos automáticamente
        self.segundoPlano = QtCore.QTimer(self)
        self.segundoPlano.timeout.connect(self.lecturas)

        # Inicialización botones
        self.btn_conectar.setText("CONECTAR")
        self.btn_capturar_luz.setText("Capturar Luminosidad")
        self.btn_focos.setText("Encender LEDs")
        self.txt_estado.setText("DESCONECTADO")

        # Conexión de botones
        self.btn_conectar.clicked.connect(self.accion)
        self.btn_capturar_luz.clicked.connect(self.toggle_captura)
        self.btn_focos.clicked.connect(self.control_focos)
        self.btn_guardar.clicked.connect(self.guardar_csv)
        self.btn_regresar.clicked.connect(self.salir)
        self.btn_capturar_luz_2.clicked.connect(self.detener_captura)

    def accion(self):
        texto = self.btn_conectar.text().upper()
        if texto == "CONECTAR":
            puerto = f"COM{self.com.text().strip()}"
            try:
                self.arduino = placa.Serial(puerto, baudrate=9600, timeout=1)
                self.btn_conectar.setText("DESCONECTAR")
                self.txt_estado.setText("CONECTADO")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo conectar al Arduino:\n{e}")
        else:
            if self.segundoPlano.isActive():
                self.segundoPlano.stop()
                self.btn_capturar_luz.setText("Capturar Luminosidad")
            if self.arduino and self.arduino.isOpen():
                self.arduino.close()
            self.btn_conectar.setText("CONECTAR")
            self.txt_estado.setText("DESCONECTADO")

    def toggle_captura(self):
        if not self.arduino or not self.arduino.isOpen():
            QtWidgets.QMessageBox.warning(self, "Error", "No estás conectado al Arduino.")
            return

        if not self.segundoPlano.isActive():
            self.segundoPlano.start(300)
            self.btn_capturar_luz.setText("Detener Datos")
        else:
            self.segundoPlano.stop()
            self.btn_capturar_luz.setText("Capturar Luminosidad")

    def detener_captura(self):
        self.segundoPlano.stop()
        self.btn_capturar_luz.setText("Capturar Luminosidad")

    def lecturas(self):
        if self.arduino and self.arduino.inWaiting():
            try:
                lectura = self.arduino.readline().decode().strip()
                if lectura:
                    self.listLuminosidad.addItem(lectura)
                    self.valores.append(lectura)
                    self.listLuminosidad.setCurrentRow(self.listLuminosidad.count() - 1)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Fallo al leer del Arduino:\n{e}")
                self.segundoPlano.stop()
                self.btn_capturar_luz.setText("Capturar Luminosidad")

    def control_focos(self):
        if not (self.arduino and self.arduino.isOpen()):
            QtWidgets.QMessageBox.warning(self, "Error", "No estás conectado al Arduino.")
            return
        try:
            if not self.focos_encendidos:
                self.arduino.write(b"1")
                self.btn_focos.setText("Apagar LEDs")
                self.focos_encendidos = True
            else:
                self.arduino.write(b"0")
                self.btn_focos.setText("Encender LEDs")
                self.focos_encendidos = False
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"No se pudo enviar el comando:\n{e}")

    def guardar_csv(self):
        try:
            with open("luminosidad.csv", "w", newline='') as archivo:
                writer = csv.writer(archivo)
                writer.writerow(["Valor LDR"])
                for v in self.valores:
                    writer.writerow([v])
            QtWidgets.QMessageBox.information(self, "Guardado", "Datos guardados en 'luminosidad.csv'")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"No se pudo guardar:\n{e}")

    def salir(self):
        if self.segundoPlano.isActive():
            self.segundoPlano.stop()
        if self.arduino and self.arduino.isOpen():
            self.arduino.close()
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ventana = MyDialog()
    ventana.show()
    sys.exit(app.exec_())
