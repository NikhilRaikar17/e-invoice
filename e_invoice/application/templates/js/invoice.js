var customer_data = document.getElementById("clear_customer_data");
var cust_name = document.getElementById("customers-name");
var address = document.getElementById("address");
var email = document.getElementById("email");
var phone_number = document.getElementById("phone_number");
var table = document.getElementById("products_table");
var table_header = document.getElementById("products_table_header");
var table_body = document.getElementById("products-table-body");
var sender_information = document.getElementById("sender_information");
var total_amount = document.getElementById("total_amount");
var sub_total = document.getElementById("sub_total");
var print = document.getElementById("print");
var export_file = document.getElementById("export_file");
var total = 0


function fill_invoice_form(){
    // Fills the invoice form with customers data
    var selected_value = select_customers.options[select_customers.selectedIndex].value;
    add_products.disabled = true;
    if (selected_value != '-1') {
        $.ajax({
            type: "GET",
            url: "{{url_for('invoice.get_customer_details')}}",
            data: {"customer_id":   selected_value },
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(result){
                if (!result["ERROR"]){
                    cust_name.childNodes[1].innerHTML = `<span style="color:#373756;">${result["name"]}</span>`;
                    address.innerHTML = `<i class="fa-solid fa-address-card"></i> - ${result["address"]}`
                    email.innerHTML = `<i class="fa-solid fa-at"></i> - ${result["email"]}`
                    phone_number.innerHTML = `<i class="fas fa-phone"></i> - ${result["phone_number"]}`
                    add_products.disabled = !add_products.disabled;
                    print.disabled = !print.disabled;
                    export_file.disabled = !export_file.disabled;
                } else{
                    add_products.disabled = true;
                    print.disabled = true;
                    export_file.disabled = true;
                }
            }
        });
    }
    if (selected_value == '-1') {
        cust_name.childNodes[1].innerHTML = `<button  class="btn btn-sm btn-light text-capitalize border-0"
                                                data-toggle="modal"
                                                data-title="Add"
                                                data-target="#select-customer"
                                                data-mdb-ripple-color="dark"
                                                >
                                                <i class="fa-solid fa-user" style="color: #373756;"></i>
                                                Select Customer
                                            </button>`;
        address.innerHTML = `<i class="fa-solid fa-address-card"></i>`
        email.innerHTML = `<i class="fa-solid fa-at"></i>`
        phone_number.innerHTML = `<i class="fas fa-phone"></i>`
        add_products.disabled = true;
        print.disabled = true;
        export_file.disabled = true;

    }
}

function update_table_with_products(){
    // Update the table with products
    var selected = [];
    var product_quantity = document.getElementById("product_quantity");
    var product_quantity_error_span = document.getElementById("product_quantity_error_span")
    if (!product_quantity.value){
        product_quantity_error_span.style.display = 'block';
    } else {
        product_quantity_error_span.style.display = 'none';

        for (var option of select_products.options) {
            if (option.selected) {
                var final_amount = parseInt(option.getAttribute("product_price")) * parseInt(product_quantity.value)
                selected.push([option.text,parseInt(product_quantity.value),
                option.getAttribute("product_price"), final_amount]);
            }
        }


        for (j = 0; j < selected.length; j++) {
            var tr_id = selected[j][0];
            total = total + parseInt(selected[j][3])
            var has_element = document.querySelectorAll("tr[id='" + tr_id + "']")
            if (has_element.length > 0) {
                var quantity = parseInt(has_element[0].childNodes[2].textContent);
                var unit_price = parseInt(has_element[0].childNodes[3].textContent);
                var amount = parseInt(has_element[0].childNodes[4].textContent);

                quantity = quantity + parseInt(product_quantity.value);
                has_element[0].childNodes[2].textContent = quantity;

                amount = quantity * unit_price;
                has_element[0].childNodes[4].textContent = amount;

            }

            else{
                var tbodyTr = document.createElement('tr');
                var tbodyTh = document.createElement('th');
                tbodyTh.scope="row"
                tbodyTh.textContent = j + 1
                tbodyTr.id=selected[j][0];
                tbodyTr.appendChild(tbodyTh);

                for (k = 0; k < selected[j].length; k++) {
                    var tbodyTd = document.createElement('td');
                    tbodyTd.innerHTML = selected[j][k];
                    tbodyTr.appendChild(tbodyTd);
                }

                var tbodyTd_delete = document.createElement('td');
                tbodyTd_delete.innerHTML = `<i class="fa-solid fa-trash" href='#' id="delete_${tr_id}" onclick="delete_product(this)" style="color:red;"></i>`
                tbodyTr.appendChild(tbodyTd_delete);
                table_body.appendChild(tbodyTr);
            }

            $('#select_products').selectpicker('deselectAll');
            table.appendChild(table_body);
            total_amount.classList.remove('d-none');
            total_amount.childNodes[1].childNodes[1].childNodes[2].textContent = "$" + total;
            var amount = total + parseInt(111);
            total_amount.childNodes[1].childNodes[5].childNodes[2].textContent = "$" + amount;
            $('#add_products_invoice').modal('hide');
        }
    }
}


function delete_product(product_id){
    var id_to_delete = '#' + product_id.getAttribute('id').replace('delete_','')
    $('#delete_added_product .modal-footer .delete_button_product').on("click", function(){
       $(id_to_delete).remove();
       recalculate_price();
       $('#delete_added_product').modal('hide');
    });

    $('#delete_added_product').modal('show');
}

function recalculate_price(){
    $('#products_table > tbody  > tr').each(function(index, tr) {
        console.log(index);
        console.log(tr);
    });
}
