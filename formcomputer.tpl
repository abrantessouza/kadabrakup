% include('default.tpl', title='KadabraKup Network')
<div class="container">
	<div class="starter-template">	
		<form method='POST' action='/savecomputer' class="form-horizontal">

		<input id="idpc" name="idcomputador" type="hidden" value="{{idCp}}">
		<fieldset>

		<!-- Form Name -->
		<legend>Computador Remoto</legend>

		<!-- Text input-->
		
		%for r in results:
			%if r[0] != "":
				<a href = '/editar/{{r[0]}}'><button type="button"  class="btn  btn-primary">Edição Básica</button></a>
				<a href = '/folders/{{r[0]}}'><button type="button"  class="btn  btn-primary">Pastas à Copiar</button></a>
			%end
			<div class="form-group">
				  <label class="col-md-4 control-label" for="computador">Nome (Alias)</label>  
				  <div class="col-md-5">
				  <input id="computador" name="computador" type="text" value="{{r[1]}}" placeholder="Nomo do Computador" class="form-control input-md" required="">			
				  </div>
			</div>
			<!-- Text input-->
			<div class="form-group">
				<label class="col-md-4 control-label" for="destino">Destino</label>  
				<div class="col-md-6">
					<input id="destino" name="destino" type="text" value="{{r[2]}}" placeholder="Endereço de Destino"  class="form-control input-md" required="">
					<span class="help-block">Endereço de Destino onde os arquivos serão salvos.</span>  
				</div>
					<label class="col-md-4 control-label" for="destino">Backup Pesado</label>
				<div class="col-md-6">
				%if r[4] == 1:
					<input type="checkbox" name="heavy" value="1" checked >
				%else:
					<input type="checkbox" name="heavy" value="1"  >
					<span class="help-block">Marque se o computador remoto possui um grande volume de arquivos</span>  
				</div>
			</div>
		%end
		<!-- Button -->
		<div class="form-group">
			  <label class="col-md-4 control-label" for="savecomputer"></label>
			  <div class="col-md-4">
				<button id="savecomputer" name="savecomputer" class="btn btn-danger">Salvar</button>
			  </div>
		</div>
	</fieldset>
	</form>
	</div>
</div>