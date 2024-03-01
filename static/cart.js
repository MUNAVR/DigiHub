$(document).ready(function () {
    $(".qty-up, .qty-down").on("click", function (e) {
        e.preventDefault();
        var $button = $(this);
        var oldValue = parseInt($button.siblings(".qty-val").text());
        var newValue;
        var maxQuantity = 3; // Maximum quantity allowed
        var cartItemId = $button.data("cartitemid");
        
        if ($button.hasClass("qty-up")) {
            newValue = oldValue < maxQuantity ? oldValue + 1 : oldValue;
        } else {
            newValue = oldValue > 1 ? oldValue - 1 : oldValue;
        }
        
        // Update quantity display
        $("#qty-" + cartItemId).text(newValue);
        
        // Send AJAX request to update quantity in the backend
        $.ajax({
            type: "POST",
            url: "{% url 'update_cart_quantity' %}",
            data: {
                csrfmiddlewaretoken: "{{ csrf_token }}",
                cart_item_id: cartItemId,
                quantity: newValue
            },

            success: function (data) {
                // Update quantity display
                $("#qty-" + cartItemId).text(data.quantity);
                // Update subtotal display after successful quantity update
                $("#subtotal-" + cartItemId).text(data.subtotal.toFixed(2));
                // Update cart totals
                updateCartTotals();
            },

            error: function (xhr, textStatus, errorThrown) {
                console.log("Error:", errorThrown);
            }
        });
    });

    function updateCartTotals() {
        $.ajax({
            type: "GET",
            url: "{% url 'get_cart_totals' %}",
            success: function (data) {
                $("#total-subtotal").text(data.total_subtotal.toFixed(2));
                // You can update other cart totals here if needed
            },
            error: function (xhr, textStatus, errorThrown) {
                console.log("Error:", errorThrown);
            }
        });
    }
});
