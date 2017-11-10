$(function () {
	$('form[name="contact"]').submit(function () {
		var $this = $(this);
		var message = $this.find('input[name="messagetext"]').val();
		if (mesage === "") {
			alert('Поле "Сообщение" не должно быть пустым.');
		} else {
			alert('Ваше сообщение отправлено!');
		}
	});
});
