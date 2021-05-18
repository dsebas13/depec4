$(document).on('ready', funcPrincipal);

function funcPrincipal()
{
    $("#btnNuevoAlineamiento").on('click', funcNuevoAlineamiento);
}

function funcNuevoAlineamiento()
{
    $("#tablaAlineamientos")
    .append
    (
        $('<tr>')
        .append
        (
            $('<td>')
            .append
            (
                $('<input>').attr('type','text').addClass('form-control')
            )
        )
        .append
        (
            $('<td>')
            .append
            (
                $('<input>').attr('type','text').addClass('form-control')
            )
        )
        .append
        (
            $('<td>').addClass('text-center')
            .append
            (
                $('<div>').addClass('btn btn-prymary').text('Guardar')
            )
            .append
            (
                $('<div>').addClass('btn btn-danger').text('Eliminar')
            )
        )
    )
}