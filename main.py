from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import gradio as gr
import re

# Carrega o modelo e o processador apenas uma vez
processor = TrOCRProcessor.from_pretrained('microsoft/trocr-large-printed')
model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-large-printed')

# Função para corrigir e validar a expressão
def corrigir_e_validar_expressao(expressao):
    # Substituições de caracteres ambíguos
    expressao = expressao.replace("x", "*").replace("X", "*")
    expressao = expressao.replace("l", "1").replace("I", "1")
    expressao = expressao.replace("O", "0").replace("o", "0")
    expressao = expressao.replace(",", ".")
    
    # Remove caracteres inválidos
    expressao = re.sub(r"[^0-9\+\-\*/\.\(\)]", "", expressao)
    
    # Valida a sintaxe básica da expressão
    try:
        eval(expressao)  # Apenas para verificar a validade
    except:
        raise ValueError("Expressão inválida ou não reconhecida.")
    
    return expressao

# Função principal
def reconhecer_e_avaliar(imagem):
    try:
        # Converte a imagem
        imagem = imagem.convert("RGB")
        # Processa com o modelo
        pixel_values = processor(images=imagem, return_tensors="pt").pixel_values
        generated_ids = model.generate(pixel_values)
        texto = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

        # Limpeza, correção e avaliação da expressão
        expressao = texto.replace(" ", "")
        expressao_corrigida = corrigir_e_validar_expressao(expressao)
        resultado = eval(expressao_corrigida)

        return f"Expressão reconhecida: {texto}\nExpressão corrigida: {expressao_corrigida}\nResultado: {resultado}"
    except Exception as e:
        return f"Erro: {str(e)}"

# Interface do Gradio
interface = gr.Interface(
    fn=reconhecer_e_avaliar,
    inputs=gr.Image(type="pil", label="Imagem com expressão"),
    outputs="text",
    title="Reconhecimento e Avaliação de Expressões com IA",
    description="Carregue uma imagem com uma expressão matemática. A IA vai reconhecer e resolver."
)

# Executa o app
interface.launch()