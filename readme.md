# Micro-ETL SIGRID – **Servicio de Restauración**

Este repositorio contiene el **primer micro-servicio** del flujo ETL:

```
┌───────────────┐      1. restaura .bak            ┌────────────────────────────┐
│ **etl_restore** │ ───────────────────────────────► │ SQL Server (TemporaryDB) │
└───────────────┘                                     └────────────────────────────┘
               ▲
               │ 2. (futuro) etl_transform extrae, transforma y carga a PostgreSQL
```

El micro-servicio **`etl_restore`**:

1. Mapea la carpeta compartida `\\192.168.14.243\tecnologia`.  
2. Busca el ZIP más reciente cuyo nombre **no** contenga `rep`.  
3. Lo copia a `C:\SQLBackups`, elimina `.bak` antiguos, lo extrae y borra el ZIP.  
4. Restaura el backup sobre la base `TemporaryDB` **usando autenticación integrada**  
   (`Trusted_Connection=yes; WITH REPLACE`).

---

## 📂 Estructura de carpetas

```
project-root/
│
├─ main.py                      # entry-point único del micro-servicio
├─ .env                         # variables de entorno (no subir a VCS)
├─ requirements.txt
│
└─ etl_restore/
   ├─ application/
   │  ├─ pipeline.py            # orquesta los pasos
   │  └─ use_cases/
   │      ├─ select_zip_use_case.py
   │      ├─ copy_and_extract_use_case.py
   │      └─ restore_database_use_case.py
   ├─ infrastructure/
   │  ├─ config.py
   │  └─ fs_gateway.py          # net use mount / unmount
   └─ ...
interface_adapters/
└─ controllers/
   └─ restore_sql_database_use_case.py
```

---

## ⚙️ Prerequisitos

| Requisito | Versión mínima | Notas |
|-----------|---------------|-------|
| **Windows 10/11** | 64-bit | Necesario para `net use` y ODBC. |
| **SQL Server** | 2016 o ↑ | Instancia `MSSQLSERVER01` en modo autenticación Windows o mixta. |
| **Microsoft ODBC Driver 17 for SQL Server** | 17.xx | <https://aka.ms/odbcdriver17> |
| **Python** | 3.12 | Crear venv. |
| **PIP deps** | ver `requirements.txt` | `pip install -r requirements.txt` |

---

## 🔑 Configuración (.env)

```ini
# SQL Server (autenticación integrada ➜ no poner usuario/clave)
SQL_SERVER=localhost\MSSQLSERVER01
SQL_DATABASE=TemporaryDB
SQL_DRIVER=ODBC Driver 17 for SQL Server
INTEGRATED_AUTH=true

# Carpetas
LOCAL_BAK_FOLDER=C:\SQLBackups
SHARED_ZIP_FOLDER=\\192.168.14.243\tecnologia

# Credenciales del share de red
NETWORK_SHARE_USER=utec
NETWORK_SHARE_PASSWORD=#Gkb.6w-ebx
```

---

## ▶️ Ejecución

```powershell
# 1. crear entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. lanzar micro-servicio
python main.py
```

### Output esperado (resumen)

```
... INICIO PIPELINE RESTORE (.bak) ...
⓪ Share de red montado OK
① ZIP seleccionado: ruesma20250630.zip
② .bak preparado: C:\SQLBackups\ruesma20250630.bak
③ Restaurando BD 'TemporaryDB'…
BD restaurada correctamente ✅
===== PIPELINE RESTORE FINALIZADO ✅ =====
🏁 Proceso de restauración COMPLETADO sin errores
```

---

## 🧪 Smoke-test opcional

`test_restore.py` comprueba:

1. Driver ODBC + conexión.
2. Restaura el `.bak` más reciente sin pasar por el ZIP.

```powershell
python test_restore.py
```

---

## 📝 Registro (logs)

* Se configura en `main.py` (`logging.basicConfig` – nivel **INFO**).  
* Cada paso importante emite un mensaje; las excepciones se muestran con
  `exc_info=True` para ver tracebacks completos.  
* Cambia el nivel a **DEBUG** para más detalle.

---

## 🚑 Solución de problemas

| Mensaje de error | Causa | Acción |
|------------------|-------|--------|
| `Driver 'ODBC Driver 17...' no instalado` | Falta driver ODBC | Instalar desde enlace oficial. |
| `Login failed for user ... (18456)` | La cuenta Windows no tiene permiso | Otorgar login o añadir al rol `sysadmin`. |
| `Network path not found` | Share no accesible / credenciales incorrectas | Verificar ruta y datos en `.env`. |
| `❌ Restauración fallida: ...` | `sqlcmd` devolvió error | Revisa permisos de archivos `.bak`, espacio en disco, nombres lógicos, etc. |


## 📝 Licencia

Proyecto interno – uso restringido.
