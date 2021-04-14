from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL


#mySql conection
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'flaskcontacts'
mysql = MySQL(app)

# settings
app.secret_key = 'mysecretkey'

@app.route('/')
def Index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts')
    data = cur.fetchall()
    return render_template('index.html', contacts = data)

@app.route('/grid')
def grid():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts')
    data = cur.fetchall()
    return render_template('grid.html', contacts = data)

@app.route('/gridjobs')
def gridjobs():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM trabajos')
    data = cur.fetchall()
    return render_template('gridjobs.html', trabajos = data)

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
        cur.execute('INSERT INTO contacts (nombre, apellido, dni, telefono, email, birthdate, idioma, niveloral, nivelescrito) VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s)',
        (nombre, apellido, dni, telefono, email, birthdate, idioma, niveloral, nivelescrito))
        mysql.connection.commit()
        flash('Contact Added succefully')
        return redirect(url_for('Index'))


@app.route('/edit/<string:id>')
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts WHERE id = {0}'.format(id))
    data = cur.fetchall()
    return render_template('edit-contact.html', contact = data[0])

@app.route('/update/<string:id>', methods = ['POST'])
def updatet_contact(id):
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
            
@app.route('/delete/<string:id>')
def delete_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contacts WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Contact Removed Successfully')
    return redirect(url_for('grid'))

if __name__ == '__main__':
    app.run(port = 3000, debug = True)




