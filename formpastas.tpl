% include('default.tpl', title='KadabraKup Network')
<div class="container">
	<div class="starter-template">	
		<form method='POST' action='/savefolder' class="form-horizontal">

		<input id="idpc" name="idcomputador" type="hidden" value="{{idComputador}}">
		<fieldset>

		<!-- Form Name -->
		<legend>Computador Remoto -> {{acao}} ->{{computador}}</legend>

		<!-- Text input-->
		
		%for r in results:
			%if r[0] != "":
				<a href = '/editar/{{r[0]}}'><button type="button"  class="btn  btn-primary">Edição Básica</button></a>
				<a href = '/folders/{{r[0]}}'><button type="button"  class="btn  btn-primary">Pastas à Copiar</button></a>
			%end
			<div class="form-group">
				  <input id="idpasta" name="idpasta" type="hidden" value="{{r[0]}}">
				  <label class="col-md-4 control-label" for="computador">Pasta</label>  
				  <div class="col-md-5">
				  <input id="computador" name="source" type="text" value="{{r[1]}}" placeholder="Endereço da pasta" class="form-control input-md" required="">			
				  <span class="help-block">Endereço de pasta que deve ser copiada.</span>  
				  </div>
			</div>
			
		%end
		<!-- Button -->
		<div class="form-group">
			  <label class="col-md-4 control-label" for="savecomputer"></label>
			  <div class="col-md-4">
				<button id="savefolder" name="savefolder" class="btn btn-danger">Salvar</button>
			  </div>
		</div>
	</fieldset>
	</form>
	</div>
</div>