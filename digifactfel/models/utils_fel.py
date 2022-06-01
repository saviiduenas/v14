import base64
import logging
import sys
from lxml import etree
import urllib.request as urllib2
import requests


class DatosGeneralesModel:
    def __init__(self, tipo, fechahoraemision, codigomoneda, numero_acceso=None, is_exportacion=False):
        self.tipo = tipo
        self.fechahoraemision = fechahoraemision
        self.codigomoneda = codigomoneda
        self.numero_acceso = numero_acceso
        self.is_exportacion = is_exportacion

    def __str__(self):
        return "DatosGeneralesModel(tipo={}, fechahoraemision={}, codigomoneda={}, numero_acceso={}, is_exportacion={})".format(
            self.tipo, self.fechahoraemision, self.codigomoneda, self.numero_acceso, self.is_exportacion)


    def to_xml(self, owner, dte_ns):
        datos_generales = etree.SubElement(
            owner,
            dte_ns + "DatosGenerales",
            attrib={
                "Tipo": self.tipo,
                "FechaHoraEmision": self.fechahoraemision,
                "CodigoMoneda": self.codigomoneda,
            },
        )                  
        if self.numero_acceso:
            datos_generales.attrib["NumeroAcceso"] = str(self.numero_acceso)
        
        if self.is_exportacion:
            datos_generales.attrib["Exp"] = "SI"

        return datos_generales


class EmisorConfigModel:
    def __init__(
        self,
        nit_emisor,
        nombre_emisor,
        codigo_establecimiento,
        nombre_comercial,
        afiliacion_iva,
    ):
        self.nit_emisor = nit_emisor
        self.nombre_emisor = nombre_emisor
        self.codigo_establecimiento = codigo_establecimiento
        self.nombre_comercial = nombre_comercial
        self.afiliacion_iva = afiliacion_iva


class EmisorModel:
    def __init__(self, config, direccion, codigo_postal, municipio, departamento, pais):
        if type(config) is not EmisorConfigModel:
            raise TypeError("config must be an EmisorConfigModel")

        self.config = config
        self.direccion = direccion
        self.codigo_postal = codigo_postal
        self.municipio = municipio
        self.departamento = departamento
        self.pais = pais

    def __str__(self):
        return "Emisor: {}\nDirección: {}\nCódigo postal: {}\nMunicipio: {}\nDepartamento: {}\nPaís: {}".format(
            self.config,
            self.direccion,
            self.codigo_postal,
            self.municipio,
            self.departamento,
            self.pais,
        )

    def to_xml(self, owner, dte_ns):
        emisor = etree.SubElement(
            owner,
            dte_ns + "Emisor",
            attrib={
                "NITEmisor": self.config.nit_emisor,
                "NombreEmisor": self.config.nombre_emisor,
                "CodigoEstablecimiento": self.config.codigo_establecimiento,
                "NombreComercial": self.config.nombre_comercial,
                "AfiliacionIVA": self.config.afiliacion_iva,
            },
        )

        direccion_emisor = etree.SubElement(
            emisor,
            dte_ns + "DireccionEmisor",
        )

        childrens = [
            ("Direccion", self.direccion),
            ("CodigoPostal", self.codigo_postal),
            ("Municipio", self.municipio),
            ("Departamento", self.departamento),
            ("Pais", self.pais),
        ]

        for child in childrens:
            element = etree.SubElement(direccion_emisor, dte_ns + child[0])
            element.text = child[1]

        return emisor


class ReceptorConfig:
    def __init__(self, nombre_receptor, id_receptor, correo_receptor=None):
        self.nombre_receptor = nombre_receptor
        self.id_receptor = id_receptor
        self.correo_receptor = correo_receptor


class ReceptorModel:
    def __init__(self, config, direccion, codigo_postal, municipio, departamento, pais):
        if type(config) is not ReceptorConfig:
            raise TypeError("config must be an ReceptorConfig")

        self.config = config
        self.direccion = direccion
        self.codigo_postal = codigo_postal
        self.municipio = municipio
        self.departamento = departamento
        self.pais = pais

    def __str__(self):
        return "Config: {}\nDirección: {}\nCódigo postal: {}\nMunicipio: {}\nDepartamento: {}\nPaís: {}".format(
            self.config,
            self.direccion,
            self.codigo_postal,
            self.municipio,
            self.departamento,
            self.pais,
        )

    def to_xml(self, owner, dte_ns):
        attr = {
            "NombreReceptor": str(self.config.nombre_receptor),
            "IDReceptor": self.config.id_receptor or "CF",
            "CorreoReceptor": str(self.config.correo_receptor),
        }

        if not self.config.correo_receptor:
            del attr["CorreoReceptor"]

        receptor = etree.SubElement(owner, dte_ns + "Receptor", attrib=attr)

        direccion_receptor = etree.SubElement(
            receptor,
            dte_ns + "DireccionReceptor",
        )

        childrens = [
            ("Direccion", self.direccion),
            ("CodigoPostal", self.codigo_postal),
            ("Municipio", self.municipio),
            ("Departamento", self.departamento),
            ("Pais", self.pais),
        ]

        for child in childrens:
            element = etree.SubElement(direccion_receptor, dte_ns + child[0])
            element.text = child[1]

        return receptor


class FraseConfig:
    def __init__(self, tipo_frase, codigo_escenario):
        self.tipo_frase = tipo_frase
        self.codigo_escenario = codigo_escenario

    def __str__(self) -> str:
        return "FraseConfig: \nTipo de frase: {}\nCódigo de escenario: {}".format(
            self.tipo_frase, self.codigo_escenario
        )


class FrasesModel:
    def __init__(self, frases):
        if type(frases) is not list:
            raise TypeError("frases must be a list")

        self.frases = frases

    def __str__(self):
        return "Frases: {}".format(self.frases)

    def to_xml(self, owner, dte_ns):
        NSMAPFRASE = {"dte": "http://www.sat.gob.gt/dte/fel/0.2.0"}
        frases = etree.SubElement(owner, dte_ns + "Frases", nsmap=NSMAPFRASE)
        for frase in self.frases:
            etree.SubElement(
                frases,
                dte_ns + "Frase",
                attrib={
                    "TipoFrase": frase.tipo_frase,
                    "CodigoEscenario": frase.codigo_escenario,
                },
            )
        return frases


class ItemConfig:
    def __init__(self, numero_linea, bien_o_servicio):
        self.numero_linea = numero_linea
        self.bien_o_servicio = bien_o_servicio

    def __str__(self) -> str:
        return "ItemConfig: \nNúmero de línea: {}\nBien o servicio: {}".format(
            self.numero_linea, self.bien_o_servicio
        )


class ItemImpuestoFields:
    def __init__(
        self, nombre_corto, codigo_unidad_gravable, monto_gravable, monto_impuesto
    ):
        self.nombre_corto = nombre_corto
        self.codigo_unidad_gravable = codigo_unidad_gravable
        self.monto_gravable = monto_gravable
        self.monto_impuesto = monto_impuesto

    def __str__(self) -> str:
        return "ItemImpuestoFields: \nNombre corto: {}\nCódigo unidad gravable: {}\nMonto gravable: {}\nMonto impuesto: {}".format(
            self.nombre_corto,
            self.codigo_unidad_gravable,
            self.monto_gravable,
            self.monto_impuesto,
        )

    def get_name_and_total(self):
        return {
            "nombre_corto": self.nombre_corto,
            "monto_impuesto": self.monto_impuesto,
        }


class ItemFields:
    def __init__(
        self,
        cantidad,
        unidad_medida,
        descripcion,
        precio_unitario,
        precio,
        descuento,
        total,
    ):
        self.cantidad = cantidad
        self.unidad_medida = unidad_medida
        self.descripcion = descripcion
        self.precio_unitario = precio_unitario
        self.precio = precio
        self.descuento = descuento
        self.total = total

    def __str__(self) -> str:
        return "ItemFields: \nCantidad: {}\nUnidad de medida: {}\nDescripción: {}\nPrecio unitario: {}\nPrecio: {}\nDescuento: {} \nTotal".format(
            self.cantidad,
            self.unidad_medida,
            self.descripcion,
            self.precio_unitario,
            self.precio,
            self.descuento,
            self.total,
        )


class ItemModel:
    def __init__(self, config, fields, impuestos=[]):
        if type(config) is not ItemConfig:
            raise TypeError("config must be an ItemConfig")

        if type(impuestos) is not list:
            raise TypeError("impuestos must be a list")

        self.config = config
        self.fields = fields
        self.impuestos = impuestos

    def __str__(self):
        return "Items:\nConfig: {}\nFields: {}\nImpuestos: {}".format(
            self.config,
            self.fields,
            self.impuestos,
        )

    def get_list_impuestos(self):
        impuestos_list = []
        for impuesto in self.impuestos:
            impuestos_list.append(
                {
                    "NombreCorto": impuesto.nombre_corto,
                    "CodigoUnidadGravable": impuesto.codigo_unidad_gravable,
                    "MontoGravable": impuesto.monto_gravable,
                    "MontoImpuesto": impuesto.monto_impuesto,
                }
            )
        return impuestos_list

    def to_xml(self, owner, dte_ns):
        item = etree.SubElement(
            owner,
            dte_ns + "Item",
            attrib={
                "NumeroLinea": self.config.numero_linea,
                "BienOServicio": self.config.bien_o_servicio,
            },
        )

        childrens = [
            ("Cantidad", self.fields.cantidad),
            ("UnidadMedida", self.fields.unidad_medida),
            ("Descripcion", self.fields.descripcion),
            ("PrecioUnitario", self.fields.precio_unitario),
            ("Precio", self.fields.precio),
            ("Descuento", self.fields.descuento),
        ]

        for child in childrens:
            tag_name = child[0]
            tag_value = child[1]
            tag_new = etree.SubElement(item, dte_ns + tag_name)
            tag_new.text = str(tag_value)

        if len(self.impuestos) > 0:
            impuestos_tag = etree.SubElement(item, dte_ns + "Impuestos")
            for impuesto in self.impuestos:
                impusto_childs = [
                    ("NombreCorto", impuesto.nombre_corto),
                    ("CodigoUnidadGravable", impuesto.codigo_unidad_gravable),
                    ("MontoGravable", impuesto.monto_gravable),
                    ("MontoImpuesto", impuesto.monto_impuesto),
                ]
                impuesto_tag = etree.SubElement(impuestos_tag, dte_ns + "Impuesto")
                for impuesto_child in impusto_childs:
                    tag_name = impuesto_child[0]
                    tag_value = impuesto_child[1]
                    tag_new = etree.SubElement(impuesto_tag, dte_ns + tag_name)
                    tag_new.text = str(tag_value)

        tag_total = etree.SubElement(item, dte_ns + "Total")
        tag_total.text = str(self.fields.total)
        return item


class TotalImpuestoConfig:
    def __init__(self, nombre_corto, total_monto_impuesto):
        self.nombre_corto = nombre_corto
        self.total_monto_impuesto = total_monto_impuesto

    def __str__(self):
        return "Nombre corto: {}, Total monto impuesto: {}".format(
            self.nombre_corto, self.total_monto_impuesto
        )

    def to_xml(self, owner, dte_ns):         
        total_impuesto = etree.SubElement(
            owner,
            dte_ns + "TotalImpuesto",
            attrib={
                "NombreCorto": self.nombre_corto,
                "TotalMontoImpuesto": str("{:.2f}".format(self.total_monto_impuesto)),
            },
        )
        return total_impuesto


class TotalesModel:
    def __init__(self, gran_total, impuestos=None):
        if type(gran_total) is not str:
            raise TypeError("gran_total must be a string")

        if type(impuestos) is not list:
            raise TypeError("impuestos must be a list")
        else:
            for impuesto in impuestos:
                if type(impuesto) is not TotalImpuestoConfig:
                    raise TypeError("impuestos must be a list of TotalImpuestoConfig")

        self.gran_total = gran_total
        self.impuestos = impuestos

    def __str__(self):
        return "Gran total: {}\nImpuestos: {}".format(self.gran_total, self.impuestos)

    def get_total_impuestos_agrupados(self):
        impuestos_agrupados = []
        # agrupar los impuestos por nombre corto, y totalizar
        for impuesto in self.impuestos:
            nombre_corto = str(impuesto.nombre_corto).strip().lower()             
            exist = False
            if len(impuestos_agrupados) > 0:
                exist = len(list(filter(lambda x: x["nombre_corto"] == nombre_corto, impuestos_agrupados))) <= 0
            if not exist:
                impuestos_agrupados.append(
                    {
                        "nombre_corto": impuesto.nombre_corto,
                        "total_monto_impuesto": 0,
                    }
                )         
        for impuesto in impuestos_agrupados:
            total_monto_impuesto = 0
            for impuesto_actual in self.impuestos:
                nombre_corto = str(impuesto["nombre_corto"]).lower().strip()                    
                if nombre_corto == str(impuesto_actual.nombre_corto).lower().strip():
                    total_monto_impuesto += float(impuesto_actual.total_monto_impuesto)
            impuesto["total_monto_impuesto"] = total_monto_impuesto         
        return impuestos_agrupados

    def to_xml(self, owner, dte_ns):
        totales = etree.SubElement(owner, dte_ns + "Totales")
        if self.impuestos:
            impuestos_tag = etree.SubElement(totales, dte_ns + "TotalImpuestos")
            impuestos_agrupados = self.get_total_impuestos_agrupados()             
            for impuesto in impuestos_agrupados:
                total_monto = str("{:.3f}".format(impuesto["total_monto_impuesto"]))                 
                etree.SubElement(
                    impuestos_tag,
                    dte_ns + "TotalImpuesto",
                    attrib={
                        "NombreCorto": impuesto["nombre_corto"],                         
                        "TotalMontoImpuesto": total_monto,
                    },
                )
        childrens = [("GranTotal", self.gran_total)]
        for child in childrens:
            tag_name = child[0]
            tag_value = child[1]
            tag_new = etree.SubElement(totales, dte_ns + tag_name)
            tag_new.text = str(tag_value)

        return totales


class ComplementoConfig:
    def __init__(self, uri_complemento, nombre_complemento, id_complemento=None):
        self.uri_complemento = uri_complemento
        self.nombre_complemento = nombre_complemento
        self.id_complemento = id_complemento


    def __str__(self):
        return "Uri complemento: {}, Nombre complemento: {}, Id complemento: {}".format(
            self.uri_complemento, self.nombre_complemento, self.id_complemento
        )


class ReferenciasNotaConfig:
    def __init__(
        self,
        numero_autorizacion_documento_origen,
        fecha_emision_documento_origen,
        motivo_ajuste,
        numero_documento_origen,
        serie_documento_origen,
    ):
        self.numero_autorizacion_documento_origen = numero_autorizacion_documento_origen
        self.fecha_emision_documento_origen = fecha_emision_documento_origen
        self.motivo_ajuste = motivo_ajuste
        self.numero_documento_origen = numero_documento_origen
        self.serie_documento_origen = serie_documento_origen

    def __str__(self):
        return "Numero autorizacion documento origen: {}, Fecha emision documento origen: {}, Motivo ajuste: {}, Numero documento origen: {}, Serie documento origen: {}".format(
            self.numero_autorizacion_documento_origen,
            self.fecha_emision_documento_origen,
            self.motivo_ajuste,
            self.numero_documento_origen,
            self.serie_documento_origen,
        )

    def to_xml(self, owner):
        CNO_NS = "{http://www.sat.gob.gt/face2/ComplementoReferenciaNota/0.1.0}"
        NSMAP_REF = {
            "cno": "http://www.sat.gob.gt/face2/ComplementoReferenciaNota/0.1.0"
        }

        return etree.SubElement(
            owner,
            CNO_NS + "ReferenciasNota",
            attrib={
                "Version": "1.0",
                "NumeroAutorizacionDocumentoOrigen": self.numero_autorizacion_documento_origen,
                "FechaEmisionDocumentoOrigen": self.fecha_emision_documento_origen,
                "MotivoAjuste": self.motivo_ajuste,
                "NumeroDocumentoOrigen": self.numero_documento_origen,
                "SerieDocumentoOrigen": self.serie_documento_origen,
            },
            nsmap=NSMAP_REF,
        )

class ExportacionFields:
    def __init__(
        self,
        nombre_consignatario_o_destinatario,
        direccion_consignatario_o_destinatario,
        codigo_consignatario_o_destinatario,
        nombre_comprador,
        direccion_comprador,
        codigo_comprador,
        otra_referencia,
        incoterm,
        nombre_exportador,
        codigo_exportador,
    ):
        self.nombre_consignatario_o_destinatario = nombre_consignatario_o_destinatario
        self.direccion_consignatario_o_destinatario = direccion_consignatario_o_destinatario
        self.codigo_consignatario_o_destinatario = codigo_consignatario_o_destinatario
        self.nombre_comprador = nombre_comprador
        self.direccion_comprador = direccion_comprador
        self.codigo_comprador = codigo_comprador
        self.otra_referencia = otra_referencia
        self.incoterm = incoterm
        self.nombre_exportador = nombre_exportador
        self.codigo_exportador = codigo_exportador

    def __str__(self):
        return "Nombre consignatario o destinatario: {}, Direccion consignatario o destinatario: {}, Codigo consignatario o destinatario: {}, Nombre comprador: {}, Direccion comprador: {}, Codigo comprador: {}, Otra referencia: {}, INCOTERM: {}, Nombre exportador: {}, Codigo exportador: {}".format(
            self.nombre_consignatario_o_destinatario,
            self.direccion_consignatario_o_destinatario,
            self.codigo_consignatario_o_destinatario,
            self.nombre_comprador,
            self.direccion_comprador,
            self.codigo_comprador,
            self.otra_referencia,
            self.incoterm,
            self.nombre_exportador,
            self.codigo_exportador,
        )

    def to_xml(self, owner):
        CEX_NS = "{http://www.sat.gob.gt/face2/ComplementoExportaciones/0.1.0}"
        
        NSMAP_EXP = {
            "cex": "http://www.sat.gob.gt/face2/ComplementoExportaciones/0.1.0"
        }        

        exportacion_tag = etree.SubElement(
            owner,
            CEX_NS + "Exportacion",
            attrib={},
            Version = "1",
            nsmap=NSMAP_EXP,
        )         

        etree.SubElement(exportacion_tag, CEX_NS + "NombreConsignatarioODestinatario").text = self.nombre_consignatario_o_destinatario
        etree.SubElement(exportacion_tag, CEX_NS + "DireccionConsignatarioODestinatario").text = self.direccion_consignatario_o_destinatario
        etree.SubElement(exportacion_tag, CEX_NS + "CodigoConsignatarioODestinatario").text = str(self.codigo_consignatario_o_destinatario)
        etree.SubElement(exportacion_tag, CEX_NS + "NombreComprador").text = self.nombre_comprador
        etree.SubElement(exportacion_tag, CEX_NS + "DireccionComprador").text = self.direccion_comprador
        etree.SubElement(exportacion_tag, CEX_NS + "CodigoComprador").text = self.codigo_comprador
        etree.SubElement(exportacion_tag, CEX_NS + "OtraReferencia").text = self.otra_referencia
        etree.SubElement(exportacion_tag, CEX_NS + "INCOTERM").text = self.incoterm
        etree.SubElement(exportacion_tag, CEX_NS + "NombreExportador").text = self.nombre_exportador
        etree.SubElement(exportacion_tag, CEX_NS + "CodigoExportador").text = self.codigo_exportador


class AbonoFields:     
    def __init__(self, numero_abono, fecha_vencimiento, monto_abono):
        self.numero_abono = numero_abono
        self.fecha_vencimiento = fecha_vencimiento
        self.monto_abono = monto_abono

    def __str__(self):
        return "Numero abono: {}, Fecha vencimiento: {}, Monto abono: {}".format(
            self.numero_abono,
            self.fecha_vencimiento,
            self.monto_abono,
        )

    def to_xml(self, owner):
        abono_tag = etree.SubElement(
            owner,
            "Abono",
        )

        etree.SubElement(abono_tag, "NumeroAbono").text = str(self.numero_abono)
        etree.SubElement(abono_tag, "FechaVencimiento").text = self.fecha_vencimiento
        etree.SubElement(abono_tag, "MontoAbono").text = str(self.monto_abono)



class ComplementoAbono:
    def __init__(self, config, abonos):
        self.config = config
        self.abonos = abonos

    def __str__(self):
        return "Config: {}, Abonos: {}".format(self.config, self.abonos)

    def to_xml(self, owner, dte_ns):
        props_complemento = {
            "URIComplemento": self.config.uri_complemento,
            "NombreComplemento": self.config.nombre_complemento,
        }

        if self.config.id_complemento:
            props_complemento["IDComplemento"] = self.config.id_complemento
            
        complementos = etree.SubElement(owner, dte_ns + "Complementos")


        NS = "{http://www.sat.gob.gt/dte/fel/CompCambiaria/0.1.0}"

        NSMAP_ = {
            "cfc": "http://www.sat.gob.gt/dte/fel/CompCambiaria/0.1.0"
        }

        complemento = etree.SubElement(
            complementos,
            NS + "Complemento",
            attrib=props_complemento,
            nsmap=NSMAP_,
        )

        abonos_factura_cambiaria = etree.SubElement(complemento,
            NS + "AbonosFacturaCambiaria",
            Version = "1",             
        )

        for abono in self.abonos:
            abono.to_xml(abonos_factura_cambiaria)



class ComplementoModel:
    def __init__(self, config, referencias_nota):
        if type(config) is not ComplementoConfig:
            raise TypeError("config must be a ComplementoConfig")

        if type(referencias_nota) is not list:
            raise TypeError("referencias_nota must be a list")
        else:
            for ref in referencias_nota:
                if type(ref) is not ReferenciasNotaConfig:
                    raise TypeError(
                        "referencias_nota must be a list of ReferenciasNotaConfig"
                    )

        self.config = config
        self.referencias_nota = referencias_nota

    def __str__(self):
        return "Config: {}\nReferencia nota: {}".format(
            self.config, self.referencias_nota
        )

    def to_xml(self, owner, dte_ns):
        props_complemento = {
            "URIComplemento": self.config.uri_complemento,
            "NombreComplemento": self.config.nombre_complemento,
        }

        if self.config.id_complemento:
            props_complemento["IDComplemento"] = self.config.id_complemento
            
        complementos = etree.SubElement(owner, dte_ns + "Complementos")
        complemento = etree.SubElement(
            complementos,
            dte_ns + "Complemento",
            attrib=props_complemento,
        )

        for ref in self.referencias_nota:
            ref.to_xml(complemento)

        return complementos

class ComplementoExportacionModel:
    def __init__(self, config, exportacion):
        if type(config) is not ComplementoConfig:
            raise TypeError("config must be a ComplementoExportacionConfig")

        if type(exportacion) is not ExportacionFields:
            raise TypeError("exportacion must be a Exportacion")

        self.config = config
        self.exportacion = exportacion

    def __str__(self):
        return "Config: {}\nExportacion: {}".format(
            self.config, self.exportacion
        )

    def to_xml(self, owner, dte_ns):
        props_complemento = {
            "URIComplemento": self.config.uri_complemento,
            "NombreComplemento": self.config.nombre_complemento,
        }

        if self.config.id_complemento:
            props_complemento["IDComplemento"] = self.config.id_complemento
            
        complementos = etree.SubElement(owner, dte_ns + "Complementos")
        complemento = etree.SubElement(complementos,
            dte_ns + "Complemento",
            attrib=props_complemento,
        )

        self.exportacion.to_xml(complemento)

        return complementos

class FelType:
    def __init__(self, codigo, descripcion=None, is_beta=False):
        self.codigo = codigo
        self.descripcion = descripcion
        self.is_beta = is_beta

    def __str__(self):
        return "Codigo: {}, Descripcion: {}, Is beta: {}".format(
            self.codigo, self.descripcion, self.is_beta
        )


class LoginModel:
    def __init__(self, username, password, nit):
        self.username = username
        self.password = password
        self.nit = nit

    def __str__(self):
        return "Username: {}, Password: {}, Nit: {}".format(
            self.username, self.password, self.nit
        )


class FEL:
    def __init__(
        self,
        fel_type,
        datos_generales,
        emisor,
        receptor,
        frases,
        items,
        totales,
        login,
        complemento=None,
        complemento_exportacion=None,
        complemento_abono=None,
    ):
        if type(fel_type) is not FelType:
            raise TypeError("fel_type must be a FelType")

        if type(datos_generales) is not DatosGeneralesModel:
            raise TypeError("datos_generales must be a DatosGeneralesModel")

        if type(emisor) is not EmisorModel:
            raise TypeError("emisor must be a EmisorModel")

        if type(receptor) is not ReceptorModel:
            raise TypeError("receptor must be a ReceptorModel")

        if type(frases) is not FrasesModel:
            raise TypeError("frases must be a FrasesModel")

        if type(items) is not list:
            raise TypeError("items must be a list")
        else:
            for item in items:
                if type(item) is not ItemModel:
                    raise TypeError("items must be a list of ItemModel")

        if type(totales) is not TotalesModel:
            raise TypeError("totales must be a TotalesModel")

        if type(login) is not LoginModel:
            raise TypeError("login must be a LoginModel")
        
        if complemento_exportacion:
            if type(complemento_exportacion) is not ComplementoExportacionModel:
                raise TypeError("complemento_exportacion must be a ComplementoExportacionModel")
        
        if complemento_abono:
            if type(complemento_abono) is not ComplementoAbono:
                raise TypeError("complemento_abono must be a ComplementoAbonoModel")                
            

        self.TYPES_WITH_COMPLEMENTO = ["NCRE", "NDEB"]
        self.need_complent = (fel_type.codigo in self.TYPES_WITH_COMPLEMENTO)
        self.complemento = None

        if complemento:
            if self.need_complent and type(complemento) is not ComplementoModel:
                raise TypeError("complemento must be a ComplementoModel")
            else:
                self.complemento = complemento

            if not self.need_complent:
                self.complemento = None
        else:
            if self.need_complent:
                raise ValueError("complemento is required")
        
        self.complemento_exportacion = complemento_exportacion
        self.complemento_abono = complemento_abono

        self.fel_type = fel_type
        self.datos_generales = datos_generales
        self.emisor = emisor
        self.receptor = receptor
        self.frases = frases
        self.items = items
        self.totales = totales
        self.login = login

    def __str__(self):
        return "Fel type: {}\nDatos generales: {}\nEmisor: {}\nReceptor: {}\nFrases: {}\nItems: {}\nTotales: {}\nLogin: {}\nComplemento: {}".format(
            self.fel_type,
            self.datos_generales,
            self.emisor,
            self.receptor,
            self.frases,
            self.items,
            self.totales,
            self.login,
            self.complemento,
        )

    def to_xml(self):
        try:
            attr_qname = etree.QName(
                "http://www.w3.org/2001/XMLSchema-instance", "schemaLocation"
            )
            DTE_NS = "{http://www.sat.gob.gt/dte/fel/0.2.0}"

            NSMAP = {
                "ds": "http://www.w3.org/2000/09/xmldsig#",
                "dte": "http://www.sat.gob.gt/dte/fel/0.2.0",
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            }
            if self.fel_type.codigo in ["FACT"]:
                NSMAP.pop("ds")
                gt_document = etree.Element(
                    DTE_NS + "GTDocumento",
                    Version="0.1",
                    nsmap=NSMAP,
                )
            else:
                gt_document = etree.Element(
                    DTE_NS + "GTDocumento",
                    {attr_qname: "http://www.sat.gob.gt/dte/fel/0.1.0"},
                    Version="0.1",
                    nsmap=NSMAP,
                )

            sat = etree.SubElement(gt_document, DTE_NS + "SAT", ClaseDocumento="dte")
            dte = etree.SubElement(sat, DTE_NS + "DTE", ID="DatosCertificados")
            datos_emision = etree.SubElement(
                dte, DTE_NS + "DatosEmision", ID="DatosEmision"
            )
            self.datos_generales.to_xml(datos_emision, DTE_NS)
            self.emisor.to_xml(datos_emision, DTE_NS)
            self.receptor.to_xml(datos_emision, DTE_NS)

            if self.fel_type.codigo not in ["NCRE", "NDEB"]:
                self.frases.to_xml(datos_emision, DTE_NS)

            items_tag = etree.SubElement(datos_emision, DTE_NS + "Items")
            for item in self.items:
                item.to_xml(items_tag, DTE_NS)

            self.totales.to_xml(datos_emision, DTE_NS)

            if self.need_complent:
                self.complemento.to_xml(datos_emision, DTE_NS)
            
            if self.complemento_exportacion:
                self.complemento_exportacion.to_xml(datos_emision, DTE_NS)
            
            if self.complemento_abono:
                self.complemento_abono.to_xml(datos_emision, DTE_NS)

            xmls = etree.tostring(gt_document, encoding="UTF-8")
            # xmls = xmls.decode("utf-8").enconde("utf-8")
            # xmls = xmls.decode("utf-8").replace("&", "&amp;").encode("utf-8")
            xmls_base_64 = base64.b64encode(xmls)
            return xmls, xmls_base_64
        except Exception as e:
            line = sys.exc_info()[-1].tb_lineno
            logging.info("=======================================================")
            raise Exception(
                "Error in line {}: {}".format(line, str(e))
            ) from e             

    def internet_on(self):
        try:
            urllib2.urlopen("http://www.google.com/", timeout=1)
            return True
        except urllib2.URLError:
            return False

    def get_token(self):
        url = "https://felgttestaws.digifact.com.gt/felapiv2/api/login/get_token"
        if not self.fel_type.is_beta:
            url = (
                "https://felgtaws.digifact.com.gt/gt.com.fel.api.v2/api/login/get_token"
            )

        json_data = {
            "Username": self.login.username,
            "Password": self.login.password,
        }
        headers = {"content-type": "application/json"}
        response = requests.post(url=url, json=json_data, headers=headers, verify=False)
        json = response.json()
        if json:
            if "Token" in json:
                return json["Token"]
            else:
                raise ValueError("No se encontro el token")
        else:
            raise ValueError("No se encontro el token")

    def send_xml(self):
        if self.internet_on():
            try:
                token = self.get_token()
                url = f"https://felgttestaws.digifact.com.gt/felapiv2/api/FelRequest?NIT={self.login.nit}&TIPO=CERTIFICATE_DTE_XML_TOSIGN&FORMAT=PDF"

                if not self.fel_type.is_beta:
                    url = f"https://felgtaws.digifact.com.gt/gt.com.fel.api.v2/api/FELRequest?NIT={self.login.nit}&TIPO=CERTIFICATE_DTE_XML_TOSIGN&FORMAT=PDF"
                             
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"{token}",
                }

                xmls, xmls_base_64 = self.to_xml()
                logging.info("xmls enviando!")
                logging.info(xmls)

                response = requests.post(url, data=xmls, headers=headers, verify=False)
                response_json = response.json()

                logging.info("response_json")
                logging.info(response_json)

                if response_json:
                    codigo = response_json["Codigo"]
                    if codigo == 1:
                        acuse_recibo_sat = response_json["AcuseReciboSAT"]
                        codigo_sat = response_json["CodigosSAT"]
                        response_data_1 = response_json["ResponseDATA1"]
                        response_data_2 = response_json["ResponseDATA2"]
                        response_data_3 = response_json["ResponseDATA3"]
                        numero_autorizacion = response_json["Autorizacion"]
                        serie = response_json["Serie"]
                        numero = response_json["NUMERO"]
                        back_procesor = response_json["BACKPROCESOR"]
                        return {
                            "acuse_recibo_sat": acuse_recibo_sat,
                            "codigo_sat": codigo_sat,
                            "formato_xml": response_data_1,
                            "formato_html": response_data_2,
                            "formato_pdf": response_data_3,
                            "numero_autorizacion": numero_autorizacion,
                            "serie": serie,
                            "numero": numero,
                            "back_procesor": back_procesor,
                        }
                    else:
                        mensaje_error = response_json["Mensaje"]
                        raise Exception(
                            "Error al enviar el documento. Codigo de error: {}. Mensaje: {}".format(
                                codigo, mensaje_error
                            )
                        )
                else:
                    raise Exception(
                        "Error al enviar el xml. Codigo de error: {}".format(
                            response.status_code
                        )
                    )
            except Exception as e:
                logging.error(e)                 
                line = sys.exc_info()[2].tb_lineno
                logging.info("-*=====================================")
                logging.info("EL ERROR ESTA DENTRO DE UTILS-FL.PY")
                logging.error(line)
                logging.info("-*=====================================")
                raise Exception(
                    "Error al enviar el xml. Codigo de error: {}".format(e)
                )                                 
        else:
            raise Exception("No hay conexion a internet")
