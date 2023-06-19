
var initialized = false;

window.addEventListener("paypalModalOpenedEvent", function() {

    if (!initialized) {
        initPayPalButton();
        initialized = true;
    }

    function initPayPalButton() {
        paypal.Buttons({
            style: {
                shape: 'rect',
                color: 'gold',
                layout: 'vertical',
                label: 'paypal',
            },
            createOrder: function(data, actions) {

                var paypalContainer = document.getElementById('paypal-button-container');
                var user_id = paypalContainer.getAttribute('data-user-id');

                var selectedItem = document.querySelector('input[name="option"]:checked');
                var selectedItemDescription = selectedItem.getAttribute("value");
                var selectedItemPrice = selectedItem.getAttribute("price");;

                console.log(`value = ${selectedItemDescription} price = ${selectedItemPrice}`);

                return actions.order.create({
                    purchase_units: [{
                        custom_id: user_id,
                        description: 'SMS Alerts',
                        amount: {
                            currency_code: 'USD',
                            value: selectedItemPrice,
                            breakdown: {
                                item_total: {
                                    currency_code: 'USD',
                                    value: selectedItemPrice,
                                },
                            }
                        },
                        items: [{
                            name: selectedItemDescription,
                            unit_amount: {
                                currency_code: 'USD',
                                value: selectedItemPrice,
                            },
                            quantity: '1'
                        }]

                    }],
                    application_context: {
                        brand_name: 'SMS Alert Service',
                        shipping_preference: 'NO_SHIPPING'
                    }
                });
            },
            onApprove: function(data, actions) {
                return actions.order.capture().then(function(orderData) {
                    // Full available details
                    console.log('Capture result', orderData, JSON.stringify(orderData, null, 2));

                    var thankYou = document.createElement("h3");
                    thankYou.innerText = "Thank you for your purchase!";

                    var message = document.createElement("p");
                    message.innerText = "Your account will be updated shortly.";

                    var orderNumber = document.createElement("h5");
                    orderNumber.innerText = "Order ID: " + orderData.id;

                    const modalBody = document.querySelector(".modalBody");
                    modalBody.innerHTML = ""; // clear contents
                    modalBody.style.padding = "50px 0px";
                    modalBody.appendChild(thankYou);
                    modalBody.appendChild(message);
                    modalBody.appendChild(orderNumber);
                });
            },
            onError: function(err) {
                console.log(err);
            },
        }).render('#paypal-button-container');
    }
});