% include('default.tpl', title='KadabraKup Network')
<div class="starter-template">
	<form method='POST' action='/savecomputer' class="form-horizontal">
	<fieldset>

	<!-- Form Name -->
	<legend>Computador Remoto</legend>

	<!-- Text input-->
	
	%for r in results:
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