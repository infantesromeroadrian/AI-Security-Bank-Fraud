# Configuración de Airtable para el Proyecto de Fraude Bancario

## ¿Qué necesitas?

Para conectar el proyecto a tu tabla de Airtable, necesitas dos cosas:
1. **API Key** de Airtable
2. **Base ID** de tu base "FraudBank"

## 📋 Paso 1: Obtener tu API Key

1. Ve a tu cuenta de Airtable: https://airtable.com/account
2. En la sección "API", copia tu **Personal Access Token** o **API Key**
3. Guarda este valor (lo usaremos en el paso 3)

## 🔍 Paso 2: Obtener el Base ID

### Opción A: Desde la API Documentation (Recomendado)

1. Abre tu base "FraudBank" en Airtable
2. Haz clic en el botón **"Help"** (?) en la esquina superior derecha
3. Selecciona **"API documentation"**
4. En la página que se abre, verás una URL como:
   ```
   https://api.airtable.com/v0/appAbc123Def456/FraudBank
   ```
5. El **Base ID** es la parte que empieza con `app...` (ejemplo: `appAbc123Def456`)

### Opción B: Desde la URL del navegador

1. Abre tu base "FraudBank" en Airtable
2. Mira la URL de tu navegador, se verá algo así:
   ```
   https://airtable.com/appAbc123Def456/tblXyz789/...
   ```
3. El **Base ID** es el código que empieza con `app` (ejemplo: `appAbc123Def456`)

## ⚙️ Paso 3: Configurar el archivo .env

1. Abre el archivo `.env` en la raíz del proyecto
2. Actualiza las siguientes líneas con tus valores reales:

```env
# Airtable API Configuration
API_AIRTABLE=tu_api_key_real_aqui

# Airtable Base Configuration
AIRTABLE_BASE_ID=appAbc123Def456
AIRTABLE_TABLE_NAME=FraudBank
```

**Ejemplo:**
```env
API_AIRTABLE=patAbcXyz123456789
AIRTABLE_BASE_ID=appM1x2Y3z4A5b6C7
AIRTABLE_TABLE_NAME=FraudBank
```

## ✅ Paso 4: Verificar la conexión

1. Reinicia el kernel del notebook (si ya estaba corriendo)
2. Ejecuta la celda de configuración de variables de entorno
3. Ejecuta la celda de extracción de datos
4. Deberías ver en los logs:
   ```
   🌐 Attempting to fetch data from Airtable...
   Fetching data from Airtable: FraudBank
   ✅ Successfully fetched XX records from Airtable
   ```

## 📊 Estructura de datos esperada en Airtable

Tu tabla "FraudBank" debe tener estas columnas:

| Columna             | Tipo    | Descripción                    |
|---------------------|---------|--------------------------------|
| transaction_id      | Number  | ID único de la transacción     |
| transaction_amount  | Number  | Monto de la transacción        |
| location            | Text    | Ubicación de la transacción    |
| merchant            | Text    | Nombre del comerciante         |
| age                 | Number  | Edad del cliente               |
| gender              | Text    | Género del cliente (M/F)       |
| fraud_label         | Number  | 0 = No fraude, 1 = Fraude      |

## 🔐 Seguridad

- ⚠️ **NUNCA** compartas tu API Key públicamente
- ⚠️ El archivo `.env` está en `.gitignore` para proteger tus credenciales
- ⚠️ No subas el `.env` a GitHub o repositorios públicos

## 🔄 Fallback automático

Si hay problemas con la conexión a Airtable, el sistema automáticamente:
1. Intentará usar el archivo CSV local (`data/fraud_dataset.csv`)
2. Si tampoco existe, generará datos sintéticos (10,000 registros)

Esto asegura que el proyecto siempre funcione, incluso sin conexión a Airtable.

## ❓ Problemas comunes

### Error: "Authentication failed"
- Verifica que tu API Key sea correcta
- Asegúrate de que no haya espacios antes/después de la key

### Error: "Base ID is required"
- Verifica que el Base ID comience con `app`
- Asegúrate de copiar el ID completo

### Error: "Failed to fetch data from Airtable"
- Verifica tu conexión a internet
- Confirma que la tabla "FraudBank" existe en tu base
- Verifica que tu API Key tenga permisos de lectura

## 📞 ¿Necesitas ayuda?

Si tienes problemas, revisa los logs en la carpeta `logs/` para más detalles sobre el error.

