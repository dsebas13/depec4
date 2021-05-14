from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from flask_mysqldb import MySQL
import base64
import PyPDF2
import fitz
import os
from os import remove


#mySql conection


app = Flask(__name__)
app.config["DEBUG"] = True
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'depec' 
mysql = MySQL(app) 


# settings
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['UPLOAD_FOLDER'] = './'

# HOME
#revisar
@app.route('/home')
def home():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:     
        flash('Sesion vencida o cerrada')
        return render_template('login.html')
    if session['rol'] == 1:
        cur.execute('SELECT * FROM cv')
    else:
        cur.execute('SELECT * FROM cv join usuario on cv.IdUsuario = usuario.IdUsuario WHERE dni = %s', [session['dni']])
        data = cur.fetchall()
        return render_template('home.html', cv = data, session = session)
    cur.execute('SELECT * FROM cv inner join usuario on cv.IdUsuario = usuario.IdUsuario  WHERE dni = %s', [session['dni']])
    conta = cur.fetchall()
    return render_template('home.html', session = session, cv = conta)

@app.route('/')
def my_form():
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM cv')
        data = cur.fetchall()
        return render_template('home.html', cv = data)
    else:
        return render_template('login.html')

# LOGIN
@app.route('/', methods= ['POST'])
def login():
    username = request.form['u']
    password = request.form['p']
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM usuario where email = %s and password = %s', (username, password))
    account = cur.fetchone()
    if account:
        session['loggedin'] = True
        session['id'] = account[0]
        session['username'] = account[3]
        session['name'] = account[1]
        session['surname'] = account[2]
        session['rol'] = account[6]
        session['dni'] = account[7]
        return redirect(url_for('home'))
    else:
        flash('Usuario o contraseña incorrectos')
    return render_template('login.html') 

# http://localhost:5000/profile - this will be the profile page, only accessible for loggedin users
@app.route('/profile')
def profile(): 
 # Check if account exists using MySQL
    cur = mysql.connection.cursor()
  
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cur.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cur.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# -----CV--------------------------- #
# pantalla carga cv
@app.route('/cv')
def Index():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html')
    cur.execute('SELECT direccion.IdDireccion,direccion.nombre FROM direccion group by direccion.IdDireccion order by direccion.IdDireccion')
    direc = cur.fetchall()
    cur.execute('SELECT *,DATE_ADD(fechaNacimiento,INTERVAL 18 YEAR) as mayoredad,CURRENT_DATE as hoy FROM usuario join direccion on usuario.IdUsuario=direccion.IdDireccion WHERE dni = %s', [session['dni']])
    data = cur.fetchone()
    cur.execute('SELECT * FROM atributo group by atributo order by atributo')
    atrib = cur.fetchall()
    cur.execute('SELECT * FROM nivel order by IdNivel')
    level = cur.fetchall()
    print(data)
    if data:
        return render_template('index.html', cv = data, direcccio = direc, atrib = atrib, level = level) 
    else:
        return render_template('home.html', cv = data, session = session)

# pantalla grilla cvs cargados
@app.route('/gridcv')
def gridcv():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    cur.execute('SELECT * FROM cv join usuario on cv.IdUsuario = usuario.IdUsuario')
    data = cur.fetchall()
    #cv del usuario
    cur.execute('SELECT * FROM cv join usuario on cv.IdUsuario = usuario.IdUsuario WHERE dni = %s', [session['dni']])
    datacv = cur.fetchall()
    return render_template('gridcv.html', cv = data, cvuser = datacv)

        
# pantalla edicion cv
@app.route('/edit/<string:id>')
def get_cv(id):
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    cur.execute('SELECT * FROM cv join usuario on cv.IdUsuario = usuario.IdUsuario WHERE cv.IdCV = {0}'.format(id))
    data = cur.fetchall()
    return render_template('edit-cv.html', cv = data[0])


# pantalla vista de un puesto cargado
@app.route('/viewjob/<string:id>')
def viewjob(id):
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html')
    cur.execute('SELECT *,datediff(CURRENT_DATE, fechaPublicacion) as dias FROM busqueda join direccion on busqueda.IdDireccion = direccion.IdDireccion join usuario on busqueda.IdUsuario = usuario.IdUsuario WHERE busqueda.IdBusqueda = {0}'.format(id))
    data = cur.fetchall()
    return render_template('viewjob.html', busqueda = data[0])

# pantalla puestos cargados
@app.route('/gridjobs', methods= ['GET','POST'])
def gridjobs():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    if request.form:
        if request.form['iddireccion'] == '1':
            cur.execute('SELECT *,datediff(CURRENT_DATE, fechaPublicacion) as dias,CURRENT_DATE FROM busqueda join direccion on busqueda.IdDireccion = direccion.IdDireccion order by dias')
            data = cur.fetchall()
        else:
            filtrodireccion = str(request.form['iddireccion'][:2])
            cur.execute('SELECT *,datediff(CURRENT_DATE, fechaPublicacion) as dias,CURRENT_DATE FROM busqueda join direccion on busqueda.IdDireccion = direccion.IdDireccion where busqueda.IdDireccion = %s order by dias', [filtrodireccion])
            data = cur.fetchall()
    else:
        cur.execute('SELECT *,datediff(CURRENT_DATE, fechaPublicacion) as dias,CURRENT_DATE FROM busqueda join direccion on busqueda.IdDireccion = direccion.IdDireccion order by dias')
        data = cur.fetchall()
    cur.execute('SELECT direccion.IdDireccion, direccion.nombre as dia FROM busqueda join direccion on busqueda.IdDireccion = direccion.IdDireccion where busqueda.fechaPublicacion <= CURRENT_DATE group by direccion.IdDireccion order by direccion.IdDireccion')
    direc = cur.fetchall()
    return render_template('gridjobs.html', busqueda = data, direcccio = direc)
# post nuevo puesto
@app.route('/mostrargrilla', methods= ['POST'])
def mostrargrilla():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    if request.form['iddireccion'] == '1':
        cur.execute('SELECT *,datediff(CURRENT_DATE, fechaPublicacion) as dias,CURRENT_DATE FROM busqueda join direccion on busqueda.IdDireccion = direccion.IdDireccion order by dias')
        data = cur.fetchall()
    else:
        filtrodireccion = str(request.form['iddireccion'][:2])
        cur.execute('SELECT *,datediff(CURRENT_DATE, fechaPublicacion) as dias,CURRENT_DATE FROM busqueda join direccion on busqueda.IdDireccion = direccion.IdDireccion where busqueda.IdDireccion = %s order by dias', [filtrodireccion])
        data = cur.fetchall()
    cur.execute('SELECT direccion.IdDireccion,direccion.nombre as dia FROM busqueda join direccion on busqueda.IdDireccion = direccion.IdDireccion where busqueda.fechaPublicacion <= CURRENT_DATE group by direccion.IdDireccion order by direccion.IdDireccion')
    direc = cur.fetchall()
    return render_template('gridjobs.html', busqueda = data, direcccio = direc)

# pantalla alta nuevo puestos
@app.route('/nuevopuesto')
def nuevopuesto():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    if session['rol'] == 1:
        cur.execute('SELECT *,CURRENT_DATE as dia FROM direccion')
        direc = cur.fetchall()
        cur.execute('SELECT *,CURRENT_DATE as dia, DATE_ADD(CURRENT_DATE,INTERVAL 30 DAY) as mastreinta FROM busqueda join direccion on busqueda.IdDireccion = direccion.IdDireccion')
        data = cur.fetchall()
        return render_template('nuevopuesto.html', busqueda = data, direcccio = direc )
    else:
        return render_template('home.html')  

# pantalla edicion puesto
@app.route('/editjobs/<string:id>')
def editjobs(id):
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html')
    if session['rol'] == 1:
        cur.execute('SELECT *,CURRENT_DATE as dia FROM direccion')
        direc = cur.fetchall()
        cur.execute('SELECT *,CURRENT_DATE as dia, DATE_ADD(CURRENT_DATE,INTERVAL 30 DAY) as mastreinta FROM busqueda join direccion on busqueda.IdDireccion = direccion.IdDireccion WHERE busqueda.IdBusqueda = {0}'.format(id))
        data = cur.fetchall()
        return render_template('editjobs.html', busqueda = data[0], direcccio = direc)
    else:
        return render_template('home.html')  

# post actualizacion puesto
@app.route('/updatejobs/<string:id>', methods = ['GET', 'POST'])
def updatejobs(id):
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    if request.method == 'POST':
        IdDireccion = str(request.form['iddireccion'][:2])
        puesto = request.form['puesto']
        fechaPublicacion = request.form['fecha']
        vacantes = request.form['vacantes']
        alcance = request.form['alcance']
        tareas = request.form['tareas']
        contacto = request.form['contacto']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE busqueda
            SET IdDireccion = %s,
                puesto = %s,
                fechaPublicacion = %s,
                vacantes = %s,
                alcance = %s,
                tareas = %s,
                contacto = %s
            WHERE id = %s
        """, (IdDireccion, puesto, fechaPublicacion, vacantes, alcance, tareas, contacto, id))
        mysql.connection.commit()
        flash('Puesto actualizado correctamente')
        return redirect(url_for('mygridjobs'))

# post nuevo puesto
@app.route('/addnuevopuesto', methods= ['POST'])
def addnuevopuesto():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    if session['rol'] == 1:
        if request.method == 'POST':
            IdDireccion = str(request.form['iddireccion'][:2])
            puesto = request.form['puesto']
            fechaPublicacion = request.form['fecha']
            vacantes = request.form['vacantes']
            alcance = request.form['alcance']
            tareas = request.form['tareas']
            contacto = request.form['contacto']
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO busqueda (IdDireccion, puesto, fecha, vacantes, alcance, tareas, contacto) VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (IdDireccion, puesto, fechaPublicacion, vacantes, alcance, tareas, contacto))
            mysql.connection.commit()
            flash('Puesto agregado correctamente')
            return redirect(url_for('mygridjobs'))
    else:
        return render_template('home.html')   


# post nuevo cv
@app.route('/add_cv', methods= ['POST'])
def add_cv():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    print(request.form)
    if request.method == 'POST':
        f = request.files['archivo']
        # Guardamos el archivo en el directorio "Archivos PDF"
        
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
        
        ### pdf a texto
        pdf_doc = f.filename
        documento = fitz.open(pdf_doc)
        
        for pagina in documento:
            texto = pagina.getText().encode("utf8")

        ### pdf a base 64
        with open((os.path.join(app.config['UPLOAD_FOLDER'], f.filename)), "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read())
        
        telefono = request.form['telefono']

        IdUsuario = session['id']
        IdPerfil = 1
        fechaCreacion  = datetime.now()
        CvRead = texto
        CvBase64 = encoded_string


        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO cv (telefono, IdUsuario, fechaCreacion , CvRead, CvBase64) VALUES (%s, %s, %s, %s, %s)',
        (telefono, IdUsuario, fechaCreacion , CvRead, CvBase64))
        mysql.connection.commit()
        cur.execute('SELECT IdCV FROM cv where cv.IdUsuario = %s order by IdCV desc', [session['id']])
        idCVs = cur.fetchone()

        if ((request.form['iddireccion']) or (request.form['iddireccion1']) or (request.form['iddireccion2'])):
            if request.form['iddireccion']:
                IdDireccion = request.form['iddireccion']
                FechaDesde = request.form['fechaIngreso']
                FechaHasta = request.form['fechaEgreso']
                Puesto = request.form['puesto']
                Tarea = request.form['tareas']
                IdCV = idCVs
                cur = mysql.connection.cursor()
                cur.execute('INSERT INTO cvdireccion (IdDireccion, FechaDesde, FechaHasta, Puesto, Tarea,IdCV) VALUES (%s, %s, %s, %s, %s, %s)',
                (IdDireccion, FechaDesde, FechaHasta, Puesto, Tarea, IdCV))
                mysql.connection.commit()

                if request.form['iddireccion1']:
                    IdDireccion = request.form['iddireccion1']
                    FechaDesde = request.form['fechaIngreso1']
                    FechaHasta = request.form['fechaEgreso1']
                    Puesto = request.form['puesto1']
                    Tarea = request.form['tareas1']
                    IdCV = idCVs
                    cur = mysql.connection.cursor()
                    cur.execute('INSERT INTO cvdireccion (IdDireccion, FechaDesde, FechaHasta, Puesto, Tarea, IdCV) VALUES (%s, %s, %s, %s, %s, %s)',
                    (IdDireccion, FechaDesde, FechaHasta, Puesto, Tarea, IdCV))
                    mysql.connection.commit()

                    if request.form['iddireccion2']:
                        IdDireccion = request.form['iddireccion2']
                        FechaDesde = request.form['fechaIngreso2']
                        FechaHasta = request.form['fechaEgreso2']
                        Puesto = request.form['puesto2']
                        Tarea = request.form['tareas2']
                        IdCV = idCVs
                        cur = mysql.connection.cursor()
                        cur.execute('INSERT INTO cvdireccion (IdDireccion, FechaDesde, FechaHasta, Puesto, Tarea, IdCV) VALUES (%s, %s, %s, %s, %s, %s)',
                        (IdDireccion, FechaDesde, FechaHasta, Puesto, Tarea, IdCV))
                        mysql.connection.commit()

        if ('formcheck' in request.form): 
            print('entrocheck')    
            for f in request.form.getlist('formcheck'):
                IdCV = idCVs
                IdAtributo = f

                cur = mysql.connection.cursor()
                cur.execute('INSERT INTO cvatributo (IdCV, IdAtributo) VALUES (%s, %s)',
                (IdCV, IdAtributo))
                mysql.connection.commit()

        if ((request.form['estudios']) or (request.form['estudios1']) or (request.form['estudios2'])):
            IdCV = idCVs
            IdAtributo = request.form['estudios']
            IdNivel = request.form['estado']
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO cvatributo (IdCV, IdAtributo, IdNivel) VALUES (%s, %s, %s)',
            (IdCV, IdAtributo, IdNivel))
            mysql.connection.commit()

            if request.form['estudios1']:
                IdCV = idCVs
                IdAtributo = request.form['estudios1']
                IdNivel = request.form['estado1']
                cur = mysql.connection.cursor()
                cur.execute('INSERT INTO cvatributo (IdCV, IdAtributo, IdNivel) VALUES (%s, %s, %s)',
                (IdCV, IdAtributo, IdNivel))
                mysql.connection.commit()

                if request.form['estudios2']:
                    IdCV = idCVs
                    IdAtributo = request.form['estudios2']
                    IdNivel = request.form['estado2']
                    cur = mysql.connection.cursor()
                    cur.execute('INSERT INTO cvatributo (IdCV, IdAtributo, IdNivel) VALUES (%s, %s, %s)',
                    (IdCV, IdAtributo, IdNivel))
                    mysql.connection.commit()


        if ((request.form['idioma']) or (request.form['idioma1']) or (request.form['idioma2'])):
            IdCV = idCVs
            IdAtributo = request.form['idioma']
            IdNivel = request.form['nivel']
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO cvatributo (IdCV, IdAtributo, IdNivel) VALUES (%s, %s, %s)',
            (IdCV, IdAtributo, IdNivel))
            mysql.connection.commit()

            if request.form['idioma1']:
                IdCV = idCVs
                IdAtributo = request.form['idioma1']
                IdNivel = request.form['nivel1']
                cur = mysql.connection.cursor()
                cur.execute('INSERT INTO cvatributo (IdCV, IdAtributo, IdNivel) VALUES (%s, %s, %s)',
                (IdCV, IdAtributo, IdNivel))
                mysql.connection.commit()

                if request.form['idioma2']:
                    IdCV = idCVs
                    IdAtributo = request.form['idioma2']
                    IdNivel = request.form['nivel2']
                    cur = mysql.connection.cursor()
                    cur.execute('INSERT INTO cvatributo (IdCV, IdAtributo, IdNivel) VALUES (%s, %s, %s)',
                    (IdCV, IdAtributo, IdNivel))
                    mysql.connection.commit()
            
        if ((request.form['Herramientas']) or (request.form['Herramientas1']) or (request.form['Herramientas2'])):
            IdCV = idCVs
            IdAtributo = request.form['Herramientas']
            IdNivel = request.form['niveltecnico']
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO cvatributo (IdCV, IdAtributo, IdNivel) VALUES (%s, %s, %s)',
            (IdCV, IdAtributo, IdNivel))
            mysql.connection.commit()

            if request.form['Herramientas1']:
                IdCV = idCVs
                IdAtributo = request.form['Herramientas1']
                IdNivel = request.form['niveltecnico1']
                cur = mysql.connection.cursor()
                cur.execute('INSERT INTO cvatributo (IdCV, IdAtributo, IdNivel) VALUES (%s, %s, %s)',
                (IdCV, IdAtributo, IdNivel))
                mysql.connection.commit()

                if request.form['Herramientas2']:
                    IdCV = idCVs
                    IdAtributo = request.form['Herramientas2']
                    IdNivel = request.form['niveltecnico2']
                    cur = mysql.connection.cursor()
                    cur.execute('INSERT INTO cvatributo (IdCV, IdAtributo, IdNivel) VALUES (%s, %s, %s)',
                    (IdCV, IdAtributo, IdNivel))
                    mysql.connection.commit()

            
        flash('Curriculum agregado correctamente')
        return redirect(url_for('Index'))


# post actualizacion cv
@app.route('/updatecv/<string:id>', methods = ['POST'])
def updatecv(id):
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        dni = request.form['dni']
        telefono = request.form['telefono']
        email = request.form['email']
        birthdate = request.form['birthdate']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE cv
            SET nombre = %s,
                apellido = %s,
                dni = %s,
                telefono = %s,
                email = %s,
                birthdate = %s
            WHERE id = %s
        """, (nombre, apellido, dni, telefono, email, birthdate, id))
        mysql.connection.commit()
        flash('Contacto actualizado correctamente')
        return redirect(url_for('gridcv'))

# borrado de cv        
@app.route('/delete/<string:id>')
def delete_cv(id):
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html')
    cur.execute('DELETE FROM cv WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Contact Removed Successfully')
    return redirect(url_for('gridcv'))

# borrado de puesto           
@app.route('/deletejobs/<string:id>')
def deletejobs(id):
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    if session['rol'] == 1:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM busqueda WHERE id = {0}'.format(id))
        mysql.connection.commit()
        flash('Puesto Removed Successfully')
        return redirect(url_for('gridjobs'))
    else:
        return render_template('home.html')

# post nueva postulacion
@app.route('/postular/<string:id>', methods= ['POST'])
def postular(id):
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    if request.method == 'POST':
        IdUsuario = session['id']
        IdBusqueda = id
        fechapostulacion = datetime.now()
        IdEstado = 1
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO postulacion (IdUsuario, IdBusqueda, fechapostulacion, IdEstado) VALUES (%s, %s, %s, %s)',
        (IdUsuario, IdBusqueda, fechapostulacion, IdEstado))
        mysql.connection.commit()
        flash('Postulacion correcta')
        return redirect(url_for('gridjobs'))

# pantalla postulaciones
@app.route('/mispostulaciones')
def mispostulaciones():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    cur.execute('SELECT *,datediff(CURRENT_DATE, busqueda.fechaPublicacion) as dias, CURRENT_DATE FROM postulacion join busqueda on postulacion.IdBusqueda = busqueda.IdBusqueda join direccion on busqueda.IdDireccion = direccion.IdDireccion where busqueda.IdUsuario = %s order by dias desc', [session['id']] )
    data = cur.fetchall()
    if data:
        return render_template('gridpostulacion.html', busqueda = data)
    else:
        return render_template('home.html')


# pantalla puestos cargados
@app.route('/mygridjobs')
def mygridjobs():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    cur.execute('SELECT *,datediff(CURRENT_DATE, fechaPublicacion) as dias,CURRENT_DATE FROM busqueda join direccion on busqueda.IdDireccion = direccion.IdDireccion where busqueda.IdUsuario = %s order by dias', [session['id']] )
    data = cur.fetchall()
    a = len(data)
    if data:
        return render_template('mygridjobs.html', busqueda = data, cantregistros = a)
    else:
        return render_template('home.html')
   
    


# logoaut
@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(port = 3000, debug = True)




