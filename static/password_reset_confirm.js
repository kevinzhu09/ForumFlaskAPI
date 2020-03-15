function getURLParameter(sParam) {
    const sPageURL = window.location.search.substring(1);
    const sURLVariables = sPageURL.split('&');
    for (let i = 0; i < sURLVariables.length; i++) {
        const sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] === sParam) {
                    return sParameterName[1];
                }
            }
        }

        $(document).ready(function () {
            const token = getURLParameter('token');
            $("#submit").click(function (e) {
                e.preventDefault();
                const password = $("#password").val();
                const confirm = $("#confirm").val();
                if (password !== confirm) {
                    alert("passwords don't match!");
                    return;
                }
                $.ajax({
                    url: "/password",
                    type: "PUT",
                    contentType: "application/json",
                    dataType: "json",
                    headers: { Authorization: "Bearer " + token },
                    data: JSON.stringify({password: password}),
                    error: function (err) {
                        alert(err.status)
                    },
                    success: function (data) {
                        alert(JSON.stringify(data));
                    }
                });

            });
        });