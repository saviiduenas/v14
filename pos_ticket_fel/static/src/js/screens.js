odoo.define('pos_ticket_fel.screens', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');

var core = require('web.core');
var rpc = require('web.rpc');

var QWeb = core.qweb;
models.load_fields('res.partner','street2');
models.load_fields('res.partner','city');
models.load_fields('res.partner','country_id');

screens.ReceiptScreenWidget.include({
    render_receipt: function(){
        var order = this.pos.get_order();
        var self = this;
        console.log(order)
        rpc.query({
            model: 'pos.order',
            method: 'search_read',
            args: [[['pos_reference', '=', order.name]], []],
        }, {
            timeout: 5000,
        }).then(function (orders) {
            if (orders.length > 0) {
                console.log(orders)

                rpc.query({
                    model: 'account.invoice',
                    method: 'search_read',
                    args: [[['id', '=', orders[0]['invoice_id'][0]  ]], []],
                }, {
                    timeout: 5000,
                }).then(function (facturas) {
                    if (facturas.length > 0) {
                        console.log(facturas)

                        var receipt_env = self.get_receipt_render_env();

                        console.log(order)


                        rpc.query({
                            model: 'account.journal',
                            method: 'search_read',
                            args: [[['id', '=', facturas[0].journal_id[0]  ]], []],
                        }, {
                            timeout: 5000,
                        }).then(function (diario) {
                            console.log(diario)
                            var direccion_id = self.pos.db.get_partner_by_id(diario[0]['direccion_id'][0]);
                            console.log(direccion_id)
                            receipt_env['feel_numero_autorizacion'] = facturas[0].feel_numero_autorizacion;
                            receipt_env['feel_serie'] = facturas[0].feel_serie;
                            receipt_env['feel_numero'] = facturas[0].feel_serie;
                            receipt_env['nombre_diario'] = direccion_id.name;
                            receipt_env['direccion'] = direccion_id.street +" " + direccion_id.street2 + ", " + direccion_id.city;
                            receipt_env['certificador_fel'] = 'DIGIFACT';

                          console.log(receipt_env)
                          self.$('.pos-receipt-container').html(QWeb.render('PosTicket', receipt_env));
                        });
                        // receipt_env['feel_uuid'] = facturas[0].feel_uuid;
                        // receipt_env['feel_serie'] = facturas[0].feel_serie;
                        // receipt_env['feel_numero'] = facturas[0].feel_serie;
                        // receipt_env['certificador_fel'] = 'INFILE';
                        //
                        // console.log(receipt_env)
                        // self.$('.pos-receipt-container').html(QWeb.render('PosTicket', receipt_env));
                    }
                });



            }
        });

    }
})



});
