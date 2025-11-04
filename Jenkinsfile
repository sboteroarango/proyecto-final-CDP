// Jenkinsfile
pipeline {
    // 1. Agente de ejecución
    // Le decimos a Jenkins que puede usar cualquier agente disponible para correr este pipeline.
    agent any

    // 2. Triggers (Disparadores automáticos)
    // Esto cumple el requisito 2.2.
    // 'pollSCM' revisa tu repositorio cada 2 minutos en busca de cambios.
    // Para un trigger en 'merge' real, se necesitaría configurar un Webhook en GitHub/GitLab,
    // lo cual es un paso más avanzado. Esto es un excelente punto de partida.
    triggers {
        pollSCM('H/2 * * * *')
    }

    // 3. Etapas del Pipeline
    // Aquí definimos los pasos que se ejecutarán en orden.
    stages {
        // Etapa 1: Clonar el Repositorio (Requisito 2.1)
        // Jenkins hace esto automáticamente al leer el Jenkinsfile,
        // pero es una buena práctica tener una etapa explícita para el checkout.
        stage('Checkout') {
            steps {
                echo 'Clonando el repositorio...'
                // El comando 'checkout scm' clona la rama que activó el pipeline.
                checkout scm
            }
        }

        // Etapa 2: Integrar una Prueba (Requisito 2.3)
        // Verificamos que existan las carpetas importantes del proyecto.
        stage('Test: Verificar Estructura') {
            steps {
                echo 'Verificando la estructura de carpetas...'
                // Usamos 'bat' porque tu consola es de Windows.
                // Este comando revisa si la carpeta 'src' existe.
                // Si no existe, el 'exit 1' hará que el pipeline falle, lo cual es correcto.
                bat 'if exist src (echo "--> Carpeta src encontrada.") else (echo "--> ERROR: No se encontró la carpeta src." && exit 1)'
            }
        }

        // Etapa 3: Ejecutar un script (Opcional, demostrando el 'dir')
        // Aquí aplicamos la nota de tu tercera imagen sobre la estructura de carpetas.
        // Si algún comando necesitara ejecutarse desde fuera de la carpeta del proyecto,
        // usarías dir('..') como te indican. Aunque es poco común, así se haría:
        stage('Ejemplo con cambio de directorio') {
            steps {
                 echo 'Ejecutando desde el workspace principal...'
                 // El siguiente bloque se ejecuta un nivel "arriba" del código clonado.
                 // Esto es solo para seguir el ejemplo que te dieron.
                 dir('..') {
                     // Por ejemplo, aquí podrías listar todo el contenido del workspace.
                     bat 'dir'
                 }
            }
        }
    }

    // 4. Acciones Post-Ejecución (Requisito 2.4)
    // Este bloque se ejecuta siempre al final del pipeline, sin importar si falló o no.
    post {
        // 'always' se ejecuta siempre.
        always {
            echo 'Pipeline finalizado. Enviando notificación...'
            // Aquí iría la integración con un servicio de notificaciones (Email, Slack, etc.).
            // Por ahora, un mensaje en la consola sirve como notificación simple.
        }
        success {
            echo 'El pipeline terminó exitosamente.'
        }
        failure {
            echo 'El pipeline ha fallado.'
        }
    }
}