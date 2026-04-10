async function simularPagamento(metodo) {
    if (!reservaAtual) return;
    
    loading(true);
    
    await delay(1500);
    
    try {
        const result = await API.simularPagamento(reservaAtual.reserva_id, metodo);
        
        if (result.sucesso) {
            mostrarMensagem('✅ Pagamento realizado com sucesso! Boa sorte no sorteio!', 'success');
            fecharModalPagamento();
            
            numerosSelecionados = [];
            atualizarCarrinho();
            await carregarMapaNumeros(rifaAtualId);
            
            setTimeout(() => {
                window.location.href = 'minhas-compras.html';
            }, 2000);
        } else {
            mostrarMensagem(result.mensagem || '❌ Falha no pagamento. Tente novamente.', 'error');
        }
        
    } catch (error) {
        mostrarMensagem('Erro ao processar pagamento', 'error');
    } finally {
        loading(false);
    }
}