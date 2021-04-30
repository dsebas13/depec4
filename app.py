from flask import Flask, render_template, request, redirect, url_for, flash, session

from flask_mysqldb import MySQL

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
        cur.execute('SELECT * FROM cv join usuario on cv.id_usuario = usuario.id WHERE dni = %s', [session['dni']])
        data = cur.fetchall()
        return render_template('home.html', cv = data, session = session)
    cur.execute('SELECT * FROM cv inner join usuario on cv.id_usuario = usuario.id  WHERE dni = %s', [session['dni']])
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

# CV
# pantalla carga cv
@app.route('/cv')
def Index():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html')
    if session['rol'] == 1:
        cur.execute('SELECT *,CURRENT_DATE FROM cv')
    else:
        cur.execute('SELECT * FROM cv join usuario on cv.id_usuario = usuario.id WHERE dni = %s', [session['dni']])
        data = cur.fetchall()
        if data:
            return render_template('home.html', cv = data, session = session) 
        else:
            pass
    data = cur.fetchall()
    return render_template('index.html', cv = data)

# pantalla grilla cvs cargados
@app.route('/gridcv')
def gridcv():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    cur.execute('SELECT * FROM cv join usuario on cv.id_usuario = usuario.id')
    data = cur.fetchall()
    cur.execute('SELECT * FROM cv join usuario on cv.id_usuario = usuario.id WHERE dni = %s', [session['dni']])
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
    cur.execute('SELECT * FROM cv join usuario on cv.id_usuario = usuario.id WHERE cv.id = {0}'.format(id))
    data = cur.fetchall()
    return render_template('edit-cv.html', cv = data[0])

# pantalla puestos cargados
@app.route('/gridjobs')
def gridjobs():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    cur.execute('SELECT *,datediff(CURRENT_DATE, fecha) as dias,CURRENT_DATE FROM busqueda join direccion on id_direccion = direccion.id order by dias')
    data = cur.fetchall()
    cur.execute('SELECT direccion.id,direccion.direccion as dia FROM busqueda join direccion on busqueda.id_direccion = direccion.id where busqueda.fecha <= CURRENT_DATE group by direccion.id order by direccion.id')
    direc = cur.fetchall()
    return render_template('gridjobs.html', busqueda = data, direcccio = direc)


# pantalla vista de un puesto cargado
@app.route('/viewjob/<string:id>')
def viewjob(id):
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html')
    cur.execute('SELECT *,datediff(CURRENT_DATE, fecha) as dias FROM busqueda join direccion on id_direccion = direccion.id WHERE busqueda.id = {0}'.format(id))
    data = cur.fetchall()
    return render_template('viewjob.html', busqueda = data[0])

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
        cur.execute('SELECT *,CURRENT_DATE as dia, DATE_ADD(CURRENT_DATE,INTERVAL 30 DAY) as mastreinta FROM busqueda join direccion on id_direccion = direccion.id')
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
        cur.execute('SELECT *,CURRENT_DATE as dia, DATE_ADD(CURRENT_DATE,INTERVAL 30 DAY) as mastreinta FROM busqueda join direccion on id_direccion = direccion.id WHERE busqueda.id = {0}'.format(id))
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
        id_direccion = str(request.form['iddireccion'][:2])
        puesto = request.form['puesto']
        fecha = request.form['fecha']
        vacantes = request.form['vacantes']
        alcance = request.form['alcance']
        tareas = request.form['tareas']
        contacto = request.form['contacto']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE busqueda
            SET id_direccion = %s,
                puesto = %s,
                fecha = %s,
                vacantes = %s,
                alcance = %s,
                tareas = %s,
                contacto = %s
            WHERE id = %s
        """, (id_direccion, puesto, fecha, vacantes, alcance, tareas, contacto, id))
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
            id_direccion = str(request.form['iddireccion'][:2])
            puesto = request.form['puesto']
            fecha = request.form['fecha']
            vacantes = request.form['vacantes']
            alcance = request.form['alcance']
            tareas = request.form['tareas']
            contacto = request.form['contacto']
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO busqueda (id_direccion, puesto, fecha, vacantes, alcance, tareas, contacto) VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (id_direccion, puesto, fecha, vacantes, alcance, tareas, contacto))
            mysql.connection.commit()
            flash('Puesto agregado correctamente')
            return redirect(url_for('mygridjobs'))
    else:
        return render_template('home.html')   


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
        cur.execute('SELECT *,datediff(CURRENT_DATE, fecha) as dias,CURRENT_DATE FROM busqueda join direccion on id_direccion = direccion.id order by dias')
        data = cur.fetchall()
    else:
        filtrodireccion = str(request.form['iddireccion'][:2])
        cur.execute('SELECT *,datediff(CURRENT_DATE, fecha) as dias,CURRENT_DATE FROM busqueda join direccion on id_direccion = direccion.id where busqueda.id_direccion = %s order by dias', [filtrodireccion])
        data = cur.fetchall()
    cur.execute('SELECT direccion.id,direccion.direccion as dia FROM busqueda join direccion on busqueda.id_direccion = direccion.id where busqueda.fecha <= CURRENT_DATE group by direccion.id order by direccion.id')
    direc = cur.fetchall()
    return render_template('gridjobs.html', busqueda = data, direcccio = direc)
    



# post nuevo cv
@app.route('/add_cv', methods= ['POST'])
def add_cv():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
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
        cur.execute('INSERT INTO cv (nombre, apellido, dni, telefono, email, birthdate, idioma, niveloral, nivelescrito) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
        (nombre, apellido, dni, telefono, email, birthdate, idioma, niveloral, nivelescrito))
        mysql.connection.commit()
        flash('Contact Added succefully')
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
@app.route('/postular', methods= ['GET','POST'])
def postular():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    if request.method == 'POST':
        id_usuario = request.form['idusuario']
        id_busqueda = request.form['idbusqueda']
        fechapostulacion = date()
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO cv (id_usuario, id_busqueda, fechapostulacion) VALUES (%s, %s, %s)',
        (id_usuario, id_busqueda, fechapostulacion))
        mysql.connection.commit()
        flash('Postulacion correcta')
        return redirect(url_for('gridjob'))


# pantalla puestos cargados
@app.route('/mygridjobs')
def mygridjobs():
    cur = mysql.connection.cursor()
    if 'loggedin' in session:
        pass
    else:        
        flash('Sesion vencida o cerrada')
        return render_template('login.html') 
    cur.execute('SELECT *,datediff(CURRENT_DATE, fecha) as dias,CURRENT_DATE FROM busqueda join direccion on id_direccion = direccion.id where busqueda.id_usuario = %s order by dias', [session['id']] )
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




