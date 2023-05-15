
var initialized = false;

window.addEventListener("paypalModalOpenedEvent", function() {

    if (!initialized) {
        initPayPalButton();
        initialized = true;
    }

    function initPayPalButton() {
        var itemOptions = document.querySelector("#smart-button-container #item-options");
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
                console.log('user_id = ' + user_id);

                var selectedItemDescription = itemOptions.options[itemOptions.selectedIndex].getAttribute("value");
                var selectedItemPrice = parseFloat(itemOptions.options[itemOptions.selectedIndex].getAttribute("price"));

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

                    // Show a success message within this page, e.g.
                    const element = document.getElementById('paypal-button-container');
                    element.innerHTML = '';
                    element.innerHTML = '<h3>Order ID: ' + orderData.id + '</h3>';
                    let unitSelection = orderData.purchase_units[0].items[0].name;
                    let units = unitSelection.replace(" Alerts", "");
                    let amount = orderData.purchase_units[0].amount.value;

                    // Or go to another URL:  actions.redirect('thank_you.html');
                });
            },
            onError: function(err) {
                console.log(err);
            },
        }).render('#paypal-button-container');
    }
});