$(document).ready(function () {
	var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

	$("#AddtoCart").on('click', function (e) {
		e.preventDefault();
		var productId = this.dataset.product;
		var color = $(".coloroptions.active").attr('id');
		var size = $(".sizeoptions.active").attr('id');
		var quantity = $("#filteredQuantityChoice").val();
		
        $.ajax({
            type: 'POST',
            url: '/ajax/add-to-cart/',
            data: {
                productid: productId,
				colorid: color,
				sizeid: size,
                productqty: quantity,
                csrfmiddlewaretoken: csrftoken,
                action: 'post'
            },
            success: function (json) {
				console.log(json);
				$('#cart-qty').text(json.qty);
            },
            error: function (xhr, errmsg, err) {
				alert(err);
			}
        });
	});

	$(".cart-item-close").on('click', function (e) {
		e.preventDefault();
		var SKU = $(this).val();
		console.log("SKU:", SKU, csrftoken)

        $.ajax({
            type: 'POST',
            url: '/ajax/delete-from-cart/',
            data: {
                SKU: SKU,
                csrfmiddlewaretoken: csrftoken,
                action: 'post'
            },
            success: function (res) {
				window.location.reload();
            },
            error: function (xhr, errmsg, err) {
				alert(err);
			}
        });
	});

    $("input[name='choice-shipping']").on('click', function () {
		
		var deliv_choice = $(this).attr('id');
        window.location.href = ('/checkout/' + deliv_choice);

	});
});
	
