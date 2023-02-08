$(document).ready(function () {

	$(".form-check-input").on('click', function () {

		var _pathname = window.location.href.split("/");
		var _url = _pathname[_pathname.length - 2];
		var a = $('.rangeslider')

		var _filterObj = {};
		
		var _minPrice = a.data('from');
		var _maxPrice = a.data('to');

		_filterObj.minPrice = _minPrice;
		_filterObj.maxPrice = _maxPrice;

		

		$(".form-check-input").each(function (index, ele) {
			var _filterKey = $(this).data('filter');
			_filterObj[_filterKey] = Array.from(document.querySelectorAll('input[data-filter=' + _filterKey + ']:checked')).map(function (el) {
				return el.value;
			});
		});

		console.log(_filterObj);

		// Run Ajax
		$.ajax({
			url: '/ajax/' + _url + '/filter-data/',
			data: _filterObj,
			dataType: 'json',
			success: function (res) {
				console.log(res);
				$("#filteredProducts").html(res.product);
				
				var count = $("#filteredProducts .product-price").length;
				$('#totalproduct').text(count + ' products');
			}
		});

		
	});

	$(".coloroptions").on('click', function () {
		
		var _pathname = window.location.href.split("/");
		var _url = _pathname[_pathname.length - 2];
		var color = $(this);
		var size = $(".sizeoptions.active");

		var _filterObj = {};
		var _colorchoice = color.attr('id');
		var _sizechoice = size.attr('id');

		console.log(_sizechoice)

		_filterObj.colorChoice = _colorchoice;

		$.ajax({
			url: '/ajax/' + _url + '/color-filter-product/',
			data: _filterObj,
			dataType: 'json',
			success: function (res) {
				console.log(res);
				$("#filteredSizeChoice").html(res.size);
				
			}
		});
		
		$('#sizechoice').empty();
		$("#sizeElements").attr("style", "display:block");
		$("#quantityElements").attr("style", "display:none");
		if (!$("#AddtoCart").hasClass( "disabled" )){
			$('#AddtoCart').addClass("disabled");
		}

	});

	$("#filteredSizeChoice").on('click',".sizeoptions", function () {
		
		var _pathname = window.location.href.split("/");
		var _url = _pathname[_pathname.length - 2];
		var color = $(".coloroptions.active");
		var size = $(this);

		var _filterObj = {};
		var _colorchoice = color.attr('id');
		var _sizechoice = size.attr('id');

		_filterObj.colorChoice = _colorchoice;
		_filterObj.sizeChoice = _sizechoice;

		$.ajax({
			url: '/ajax/' + _url + '/color-size-filter-product/',
			data: _filterObj,
			dataType: 'json',
			success: function (res) {
				console.log(res);
				$("#filteredQuantityChoice").html(res.quantity);
				
			}
		});

		$('#AddtoCart').removeClass("disabled");
	});

});