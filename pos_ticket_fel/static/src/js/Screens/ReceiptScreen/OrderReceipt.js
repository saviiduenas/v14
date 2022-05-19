odoo.define('pos_ticket_fel.OrderReceipt', function(require) {
    'use strict';

    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const Registries = require('point_of_sale.Registries');
    const { useState, useContext } = owl.hooks;
    const models = require('point_of_sale.models');
    const pos_db = require('point_of_sale.DB');


    models.load_fields('account.journal','direccion_sucursal');
    models.load_fields('res.company','certificador');
    models.load_fields('account.journal','direccion_id');
    models.load_fields('account.journal','feel_tipo_dte');

    models.load_models({
        model: 'account.journal',
        fields: [],
        domain: function(self){ return []; },
        loaded: function(self,journals){
            self.direccion_diario = "";
            self.telefono = "";
            self.tipo_dte = "";
            if (journals.length > 0) {
                journals.forEach(function(journal) {
                    if ('direccion_sucursal' in journal || 'direccion' in journal){
                        self.direccion_diario = journal.direccion_sucursal;
                        if (journal.id == self.config.invoice_journal_id[0]){
                            self.direccion_diario = journal.direccion_sucursal || journal.direccion_id;
                            self.telefono = journal.telefono;
                            self.tipo_dte = journal.feel_tipo_dte;
                        }
                    }else{
                        if('direccion_id' in journal){
                            if (journal.id == self.config.invoice_journal_id[0]){
                                self.rpc({
                                  model: 'res.partner',
                                  method: 'search_read',
                                  args: [[['id', '=',   journal['direccion_id'][0]]], []],
                              }, {
                                  timeout: 5000,
                              }).then(function (direc) {
                                  self.direccion_diario = direc[0]['contact_address_complete'];
                                  self.nombre_comercial = journal.fel_nombre_comercial
                                  self.tipo_dte = journal.feel_tipo_dte;
                              });

                            }
                        }
                    }

                })

            }
        },
    });

    const PosTicketFelOrderReceipt = OrderReceipt =>
        class extends OrderReceipt {
            constructor() {
                super(...arguments);
                var order = this.env.pos.get_order();
                var self = this;
                this.state = useState({
                  'cliente_id': order.get_client(),
                  'qr_string': false,
                  // 'qr_string': "https://felgtaws.digifact.com.gt/guest/api/FEL?DATA=96524081%7CB96A30D0-22FC-44D2-8900-A4F1103A0AB7%7CGUESTUSERQR",
                  'feel_numero_autorizacion': false,
                  'feel_serie': false,
                  'feel_numero': false,
                  'nombre_diario': false,
                  'nombre_comercial': order.pos.nombre_comercial|| '',
                  'direccion': order.pos.direccion_diario,
                  'certificador': order.pos.company.certificador,
                  'telefono': order.pos.telefono,
                  'acceso': false,
                });
                var state = this.state;


                var odoo_sync = this.env.pos.get('synch');
                if (odoo_sync && 'status' in odoo_sync &&  odoo_sync['status'] == "disconnected" && order.to_invoice == true){
                    var numero_uno = "1"
                    var nuevo_uid = order.uid.replace(/[^a-zA-Z0-9 ]/g, '');
                    var acceso = parseInt(numero_uno + nuevo_uid.substr(nuevo_uid.length - 6)) + 100000000;
                    order.set_acceso(acceso);
                    state.acceso = acceso;
                }

                self.rpc({
                    model: 'pos.order',
                    method: 'search_read',
                    args: [[['pos_reference', '=', order.name]], []],
                }, {
                    timeout: 5000,
                }).then(function (orders) {
                    if (orders.length > 0 && 'account_move' in orders[0] && orders[0]['account_move'].length > 0) {
                          self.rpc({
                            model: 'account.move',
                            method: 'search_read',
                            args: [[['id', '=', orders[0]['account_move'][0]  ]], []],
                        }, {
                            timeout: 5000,
                        }).then(function (facturas) {
                            if (facturas.length > 0) {
                                  self.rpc({
                                    model: 'account.journal',
                                    method: 'search_read',
                                    args: [[['id', '=', facturas[0].journal_id[0]  ]], []],
                                }, {
                                    timeout: 5000,
                                }).then(function (diario) {
                                    state.feel_numero_autorizacion = facturas[0].feel_numero_autorizacion || facturas[0].fel_numero_autorizacion;
                                    state.feel_serie = facturas[0].feel_serie || facturas[0].fel_serie;
                                    state.feel_numero = facturas[0].feel_numero || facturas[0].fel_numero;
                                    state.direccion = self.direccion_diario;
                                    var link = "";
                                    if (state.certificador == "INFILE"){
                                        var link = ["https://report.feel.com.gt/ingfacereport/ingfacereport_documento?","uuid=",state.feel_numero_autorizacion.toString() ].join('');

                                    }else{
                                        var link = ["https://felgtaws.digifact.com.gt/guest/api/FEL?DATA=",self.env.pos.company.vat.toString(), "%", "7C", facturas[0].feel_numero_autorizacion.toString(),"%7CGUESTUSERQR"].join('');

                                    }
                                    state.qr_string = link;
                                });
                            }
                        });



                    }
                });
            }
        };

        var _super_order = models.Order.prototype;
        models.Order = models.Order.extend({
          get_acceso: function(){
              return this.get('acceso');
          },
          set_acceso: function(acceso){
              this.set('acceso', acceso);
          },

          init_from_JSON: function(json) {
              _super_order.init_from_JSON.apply(this,arguments);
              this.acceso = this.get_acceso();
          },

          export_as_JSON: function() {
              var json = _super_order.export_as_JSON.apply(this,arguments);

              var odoo_sync = this.pos.get('synch');
              if (odoo_sync && 'status' in odoo_sync &&  odoo_sync['status'] == "disconnected" && this.to_invoice == true){
                  var numero_uno = "1"
                  var nuevo_uid = this.uid.replace(/[^a-zA-Z0-9 ]/g, '');
                  this.set_acceso( parseInt(numero_uno + nuevo_uid.substr(nuevo_uid.length - 6)) + 100000000);
              }
              this.revisar_contingencias(this.pos.db.get_orders());
              json.acceso = this.get_acceso();
              return json
          },


          revisar_contingencias: function(ordenes){
              ordenes.forEach(function(orden) {
                  if (orden.to_invoice == true){
                      if (orden.data.uid){
                        var numero_uno = "1"
                        var nuevo_uid = orden.data.uid.replace(/[^a-zA-Z0-9 ]/g, '');
                        orden.data.acceso = parseInt(numero_uno + nuevo_uid.substr(nuevo_uid.length - 6)) + 100000000;
                        orden.acceso = parseInt(numero_uno + nuevo_uid.substr(nuevo_uid.length - 6)) + 100000000;
                        // this.set_acceso(parseInt(numero_uno + nuevo_uid.substr(nuevo_uid.length - 6)) + 100000000)
                      }
                  }


              });
          },


        })

    Registries.Component.extend(OrderReceipt, PosTicketFelOrderReceipt);

    return OrderReceipt;

});
