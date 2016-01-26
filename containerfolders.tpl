% include('default.tpl', title='KadabraKup Network')
 <div class="container">
	<div class="starter-template">
		 <a href = '/novapasta/{{idCp}}'><button type="button"  class="btn btn-lg btn-danger">Nova Pasta</button></a>
		 <a href = '/editar/{{idCp}}'><button type="button"  class="btn btn-lg btn-danger">Retornar</button></a>
		 <p align='center'>{{computador}}</p>
			<table border=1 class="table">
				<thead>
					<tr>
						<th  style="text-align:center">Computador</th>						
						<th  style="text-align:center">Pasta</th>
						<th  style="text-align:center">Ações</th>
					</tr>
				</thead>
				<tbody>
				%for r in results:				
					<tr>
						<td>{{r[3]}}</td>
						<td>{{r[1]}}</td>						
						<td>
						   <a href = '/editarpasta/{{r[0]}}'><button type="button" class="btn btn-xs btn-warning">Editar</button></a>						   
						   <a href = '/apagarpasta/{{r[0]}}'<button type="button" class="btn btn-xs btn-warning">Apagar</button></a>
						</td>
					</tr>
				%end	
				</tbody>
		</table>
	</div>
</div>