from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from datetime import datetime


#mySql conection
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'flaskcontacts'
mysql = MySQL(app)

# settings
app.secret_key = 'mysecretkey'

# login

@app.route('/home')
def home():
    return render_template('home.html')
 
@app.route('/')
def my_form():
    return render_template('login.html')


@app.route('/', methods= ['POST'])
def login():
    username = request.form['u']
    password = request.form['p']
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM usuarios where email = %s and password = %s', (username, password))
    account = cur.fetchone()
    if account:
        session['loggedin'] = True
        session['id'] = account[0]
        session['username'] = account[3]
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

# pantalla carga cv
@app.route('/csv')
def Index():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    cur = mysql.connection.cursor()
    cur.execute('SELECT *,CURRENT_DATE FROM contacts')
    data = cur.fetchall()
    return render_template('index.html', contacts = data)

# pantalla grilla cvs cargados
@app.route('/grid')
def grid():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    cur = mysql.connection.cursor()
    cur.execute('SELECT *,CURRENT_DATE FROM contacts')
    data = cur.fetchall()

    return render_template('grid.html', contacts = data)

# pantalla edicion cv
@app.route('/edit/<string:id>')
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts WHERE id = {0}'.format(id))
    data = cur.fetchall()
    return render_template('edit-contact.html', contacts = data[0])

# pantalla puestos cargados
@app.route('/gridjobs')
def gridjobs():
    cur = mysql.connection.cursor()
    cur.execute('SELECT *,datediff(CURRENT_DATE, fecha) as dias FROM trabajos order by dias')
    data = cur.fetchall()
    return render_template('gridjobs.html', trabajos = data)

# pantalla vista de un puesto cargado
@app.route('/viewjob/<string:id>')
def viewjob(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT *,datediff(CURRENT_DATE, fecha) as dias FROM trabajos WHERE id = {0}'.format(id))
    data = cur.fetchall()
    return render_template('viewjob.html', trabajos = data[0])

# pantalla alta nuevo puestos
@app.route('/nuevopuesto')
def nuevopuesto():
    cur = mysql.connection.cursor()
    cur.execute('SELECT *,CURRENT_DATE as hoy FROM trabajos')
    data = cur.fetchall()
    return render_template('nuevopuesto.html', trabajos = data)

# pantalla edicion puesto
@app.route('/editjobs/<string:id>')
def editjobs(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT *,CURRENT_DATE as dia FROM trabajos WHERE id = {0}'.format(id))
    data = cur.fetchall()
    return render_template('editjobs.html', trabajos = data[0])

# post nuevo puesto
@app.route('/addnuevopuesto', methods= ['POST'])
def addnuevopuesto():
    if request.method == 'POST':
        direccion = request.form['direccion']
        puesto = request.form['puesto']
        fecha = request.form['fecha']
        vacantes = request.form['vacantes']
        alcance = request.form['alcance']
        tareas = request.form['tareas']
        contacto = request.form['contacto']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO trabajos (direccion, puesto, fecha, vacantes, alcance, tareas, contacto) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        (direccion, puesto, fecha, vacantes, alcance, tareas, contacto))
        mysql.connection.commit()
        flash('Puesto agregado correctamente')
        return redirect(url_for('gridjobs'))

# post nuevo cv
@app.route('/add_contact', methods= ['POST'])
def add_contact():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        dni = request.form['dni']
        email = request.form['email']
        birthdate = request.form['birthdate']
        idioma = request.form['idioma']
        niveloral = request.form['niveloral']
        nivelescrito = request.form['nivelescrito']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO contacts (nombre, apellido, dni, telefono, email, birthdate, idioma, niveloral, nivelescrito) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
        (nombre, apellido, dni, telefono, email, birthdate, idioma, niveloral, nivelescrito))
        mysql.connection.commit()
        flash('Contact Added succefully')
        return redirect(url_for('Index'))

# post actualizacion puesto
@app.route('/updatejobs/<string:id>', methods = ['POST'])
def updatejobs(id):
    if request.method == 'POST':
        direccion = request.form['direccion']
        puesto = request.form['puesto']
        fecha = request.form['fecha']
        vacantes = request.form['vacantes']
        alcance = request.form['alcance']
        tareas = request.form['tareas']
        contacto = request.form['contacto']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE trabajos
            SET direccion = %s,
                puesto = %s,
                fecha = %s,
                vacantes = %s,
                alcance = %s,
                tareas = %s,
                contacto = %s
            WHERE id = %s
        """, (direccion, puesto, fecha, vacantes, alcance, tareas, contacto, id))
        mysql.connection.commit()
        flash('Puesto actualizado correctamente')
        return redirect(url_for('gridjobs'))

# post actualizacion cv
@app.route('/updatecontact/<string:id>', methods = ['POST'])
def updatecontact(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        dni = request.form['dni']
        telefono = request.form['telefono']
        email = request.form['email']
        birthdate = request.form['birthdate']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE contacts
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
        return redirect(url_for('grid'))

# borrado de cv           
@app.route('/delete/<string:id>')
def delete_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contacts WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Contact Removed Successfully')
    return redirect(url_for('grid'))

# borrado de puesto           
@app.route('/deletejobs/<string:id>')
def deletejobs(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM trabajos WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Puesto Removed Successfully')
    return redirect(url_for('gridjobs'))

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




