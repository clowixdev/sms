function show_hide_password(target){
	var input = document.getElementById('authToken');
    var btn = document.getElementById('btn')
	if (input.getAttribute('type') == 'password') {
		target.classList.add('view');
		input.setAttribute('type', 'text');
        btn.setAttribute('class', 'btn bi bi-eye-slash')
	} else {
		target.classList.remove('view');
		input.setAttribute('type', 'password');
        btn.setAttribute('class', 'btn bi bi-eye')
	}
	return false;
}