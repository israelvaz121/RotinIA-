async function gerarRotina() {
    const tempo = document.getElementById("tempo").value;
    const nivel = document.getElementById("nivel").value;
    const objetivo = document.getElementById("objetivo").value;

    if (!tempo || !nivel || !objetivo) {
        document.getElementById("resultadoRotina").textContent = "Por favor, preencha todos os campos.";
        return;
    }

    try {
        const resposta = await fetch("http://127.0.0.1:8000/rotina", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                tempo_disponivel: tempo,
                nivel: nivel,
                objetivo: objetivo
            })
        });

        const dados = await resposta.json();
        let resultadoFormatado = '';

        if (dados.rotina) {
            for (let dia in dados.rotina) {
                resultadoFormatado += `${dia.toUpperCase()}:\n- ${dados.rotina[dia].join('\n- ')}\n\n`;
            }
        } else if (dados.rotina_texto) {
            resultadoFormatado = dados.rotina_texto;
        } else if (dados.error) {
            resultadoFormatado = "Erro: " + dados.error;
        } else {
            resultadoFormatado = "Erro ao gerar rotina.";
        }

        document.getElementById("resultadoRotina").textContent = resultadoFormatado;
    } catch (erro) {
        console.error("Erro ao gerar rotina:", erro);
        document.getElementById("resultadoRotina").textContent = "Erro ao gerar rotina.";
    }
}