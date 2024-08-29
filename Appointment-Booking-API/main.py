from website import create_app

app = create_app()

if __name__ == '__main__': #only if we run this file will the next line be exectued
    app.run(debug=True) #starts up webserver and if we make changes to code webserver is reran
    