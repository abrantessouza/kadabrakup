% include('default.tpl', title='KadabraKup Network')

 <div class="container">
	<div class="starter-template">
		 <a href = '/novo'><button type="button"  class="btn btn-lg btn-danger">Novo Computador</button></a>
		 <a href = '/startbackup'><button type="button" {{runingBackup}}  class="btn btn-lg btn-danger">Iniciar Backup Incremental</button></a>
		 <a href = '/startfull'><button type="button" {{runingBackup}}  class="btn btn-lg btn-danger">Iniciar Backup FULL</button></a>
		 
		 <a href = '/stopbackup'><button type="button"   class="btn btn-lg btn-danger">Parar Backup</button></a>
		 
			<table border=1 class="table">
				<thead>
					<tr>
						<th  style="text-align:center">Computador</th>
						<th  style="text-align:center">Destino</th>
						<th  style="text-align:center; width: 20px;">Download</th>
						<th  style="text-align:center">Status</th>
						<th  style="text-align:center">Ignorar</th>
						<th  style="text-align:center">Ações</th>
					</tr>
				</thead>
				<tbody>
				%for r in results:				
					<tr>
						<td>{{r[1]}}</td>
						<td>{{r[2]}}</td>
						<td>{{r[6]}}</td>
						<td>{{r[3].decode("cp1252",'replace')}}
						%if "%" in str(r[3]):
								<img src="img/3.gif" width='20' height='20'>						
						%end
						</td>
						
						<td>
							%if r[5] == 1:								
								<input type="checkbox" checked="checked" onclick = "clickSend(this);" value="1" data-id={{r[0]}}>
							%else:
								<input type="checkbox"  onclick = "clickSend(this);" value="1" data-id={{r[0]}}>
							%end
						</td>
						<td>
						 <a href = '/editar/{{r[0]}}'><button type="button" {{runingBackup}} class="btn btn-xs btn-warning">Editar</button></a>
						 <a href = '/logs/{{r[0]}}'<button type="button" class="btn btn-xs btn-warning">Logs</button></a>
						 <a href = '/startfullbackup/{{r[0]}}'<button type="button" {{runingBackup}} class="btn btn-xs btn-success">Backup FULL</button></a>
						 <a href = '/apagar/{{r[0]}}'<button type="button" class="btn btn-xs btn-danger">Apagar</button></a></td>
						
					</tr>
				%end	
				</tbody>
		</table>
	</div>
</div>
<script>
setInterval(function() {
	//A cada um minuto ele faz o refreash da página
	location.reload();
	},60000);
	
function clickSend(dt){
	var ajaxRequest = new XMLHttpRequest();
	ajaxRequest.open("POST","/clickSenderIng", true);
	ajaxRequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	var id = dt.getAttribute("data-id");
	var val = 0;
	if(dt.checked){
		val = 1;
	}	
	ajaxRequest.send("idComputador="+id+"&valueFied="+val)
}


</script>