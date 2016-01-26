% include('default.tpl', title='KadabraKup Network')
 <div class="container">
	<div class="starter-template">		
			<table border=1 class="table">
				<thead>
					<tr>
						<th  style="text-align:center">Computador</th>
						<th  style="text-align:center">Mensagem</th>
						<th  style="text-align:center">Data</th>
						
					</tr>
				</thead>
				<tbody>
				%for r in results:				
					<tr>
						<td>{{r[0]}}</td>
						<td>{{r[1]}}</td>
						<td>{{r[2]}}</td>
						
				%end	
				</tbody>
		</table>
	</div>
</div>