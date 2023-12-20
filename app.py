from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['SECRET_KEY'] = 'una cadena de texto muy secreta'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'hRhki-3cqZ(]4dcs'
app.config['MYSQL_DB'] = 'libreriaonline'

mysql = MySQL()

mysql.init_app(app)

# Clase producto con conexion a la base de datos
class Producto:
    def __init__(self, id, nombre, precio, imagen=None, descripcion=None):
        self.id = id
        self.nombre = nombre
        self.precio = precio
        self.imagen = imagen
        self.descripcion = descripcion

    def guardar_en_bd(self):
     try:
        with mysql.connection.cursor() as cur:
            if self.id is None:
                cur.execute(
                    "INSERT INTO productos (nombre, precio, imagen, descripcion) VALUES (%s, %s, %s, %s)",
                    (self.nombre, self.precio, self.imagen, self.descripcion))
            else:
                cur.execute(
                    "UPDATE productos SET nombre=%s, precio=%s, imagen=%s, descripcion=%s WHERE id=%s",
                    (self.nombre, self.precio, self.imagen, self.descripcion, self.id))
        
        mysql.connection.commit()
        flash(f'Se ha guardado el producto: {self.nombre}', 'success')
     except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al guardar el producto: {str(e)}', 'error')
       

    def eliminar_de_bd(self):
        if self.id is not None:
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM productos WHERE id=%s", (self.id,))
            mysql.connection.commit()
            cur.close()

    @staticmethod
    def obtener_producto_por_id(producto_id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM productos WHERE id = %s", (producto_id,))
        data = cur.fetchone()
        cur.close()

        if data:
            return Producto(id=data[0], nombre=data[1], precio=data[2], imagen=data[3], descripcion=data[4])

        return None

    @staticmethod
    def obtener_productos_desde_bd():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM productos")
        data = cur.fetchall()
        cur.close()

        productos = []
        for row in data:
            producto = Producto(id=row[0], nombre=row[1], precio=row[2], imagen=row[3], descripcion=row[4])
            productos.append(producto)

        return productos

class CarritoForm(FlaskForm):
    cantidad = StringField('Cantidad', validators=[DataRequired()])
    submit = SubmitField('Agregar al carrito')

class ContactoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Correo electrónico', validators=[DataRequired()])
    mensaje = StringField('Mensaje', validators=[DataRequired()])
    submit = SubmitField('Enviar Mensaje')

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    precio = DecimalField('Precio', validators=[DataRequired()])
    imagen = StringField('URL de la Imagen', validators=[DataRequired()])
    descripcion = StringField('Descripción', validators=[DataRequired()])
    submit = SubmitField('Agregar/Actualizar')


@app.route('/')
def index():
    # Carga los productos desde la base de datos
    productos = Producto.obtener_productos_desde_bd()
    print(productos)  # Agrega esta línea para verificar si los productos se están recuperando
    return render_template('index.html', productos=productos, titulo='Tienda Online')

# Ruta de producto con conexion a la base de datos
@app.route('/producto/<int:id>', methods=['GET', 'POST'])
def producto(id):
    productos = Producto.obtener_productos_desde_bd()  # Obtener la lista actualizada de productos desde la base de datos
    producto = next((p for p in productos if p.id == id), None)
    if producto:
        form = CarritoForm()
        if form.validate_on_submit():
            cantidad = int(form.cantidad.data)
            carrito = session.get('carrito', [])
            item_existente = next((item for item in carrito if item['producto_id'] == producto.id), None)

            if item_existente:
                item_existente['cantidad'] += cantidad
            else:
                carrito.append({'producto_id': producto.id, 'cantidad': cantidad})

            session['carrito'] = carrito
            flash(f'Se han agregado {cantidad} {producto.nombre}(s) al carrito', 'success')
            return redirect(url_for('index'))

        return render_template('producto.html', producto=producto, form=form)
    return 'Producto no encontrado', 404


@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    form = ContactoForm()
    if form.validate_on_submit():
        flash('Mensaje enviado correctamente', 'success')
        return redirect(url_for('index'))
    return render_template('contacto.html', form=form, titulo='Contacto')

@app.route('/api',methods=['GET', 'POST'])
def api():
    return render_template('api.html', titulo='API de Libros')

## Ruta del Carrito
@app.route('/carrito')
def carrito():
    carrito = session.get('carrito', [])
    productos = Producto.obtener_productos_desde_bd()  # Obtener la lista actualizada de productos desde la base de datos
    productos_en_carrito = []
    total = 0

    for item in carrito:
        producto = next((p for p in productos if p.id == item['producto_id']), None)
        if producto:
            subtotal = producto.precio * item['cantidad']
            total += subtotal
            productos_en_carrito.append({'producto': producto, 'cantidad': item['cantidad'], 'subtotal': subtotal})

    return render_template('carrito.html', titulo='Carrito de Compras', productos_en_carrito=productos_en_carrito, total=total)

@app.route('/vaciar_carrito')
def vaciar_carrito():
    session['carrito'] = []
    flash('El carrito se ha vaciado correctamente', 'success')
    return redirect(url_for('carrito'))

# Ruta gestion de producto con conexion a la base de datos
@app.route('/gestion_productos', methods=['GET', 'POST'])
def gestion_productos():
    form = ProductoForm()

    if form.validate_on_submit():
        nuevo_producto = Producto(
            id=None,
            nombre=form.nombre.data,
            precio=form.precio.data,
            imagen=form.imagen.data,
            descripcion=form.descripcion.data
        )
        nuevo_producto.guardar_en_bd()
        flash(f'Se ha agregado un nuevo producto: {nuevo_producto.nombre}', 'success')
        return redirect(url_for('gestion_productos'))

    # Obtener productos desde la base de datos
    productos = Producto.obtener_productos_desde_bd()

    return render_template('gestion_productos.html', form=form, productos=productos, titulo='Gestión de Productos')

# Eliminar producto de la base de datos y de la app
@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):
    producto = Producto(id=id, nombre=None, precio=None, imagen=None, descripcion=None)
    producto.eliminar_de_bd()
    flash(f'Se ha eliminado el producto con ID {id}', 'success')
    return redirect(url_for('gestion_productos'))

# Editar producto de la base de datos y de la app
@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    form = ProductoForm()

    if request.method == 'GET':
        # Obtener detalles del producto desde la base de datos
        producto = Producto.obtener_producto_por_id(id)

        if producto:
            form.nombre.data = producto.nombre
            form.precio.data = producto.precio
            form.imagen.data = producto.imagen
            form.descripcion.data = producto.descripcion

    elif request.method == 'POST' and form.validate_on_submit():
        producto = Producto(
            id=id,
            nombre=form.nombre.data,
            precio=form.precio.data,
            imagen=form.imagen.data,
            descripcion=form.descripcion.data
        )
        producto.guardar_en_bd()
        flash(f'Se ha modificado el producto: {producto.nombre}', 'success')
        return redirect(url_for('gestion_productos'))

    # Obtener la lista actualizada de productos desde la base de datos
    productos = Producto.obtener_productos_desde_bd()

    return render_template('gestion_productos.html', form=form, productos=productos, titulo='Gestión de Productos')

app.run(debug=True)