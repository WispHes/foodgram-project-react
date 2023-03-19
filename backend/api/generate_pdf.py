from django.http.response import HttpResponse
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
from recipes.models import Recipe


def generate_shopping_cart_pdf(request):
    """Генерация списка покупок в виде PDF формата"""
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = ("attachment; "
                                       "filename=shopping_cart.pdf")

    p = canvas.Canvas(response)
    arial = ttfonts.TTFont("Arial", "data/arial.ttf")
    pdfmetrics.registerFont(arial)
    p.setFont("Arial", 14)

    ingredients = Recipe.objects.filter(
        author__shopping_cart__user=request.user
    ).values_list(
        "ingredients__ingredient__name",
        "ingredients__amount",
        "ingredients__ingredient__unit"
    )

    ingr_list = {}
    for name, amount, unit in ingredients:
        if name not in ingr_list:
            ingr_list[name] = {"amount": amount, "unit": unit}
        else:
            ingr_list[name]["amount"] += amount
    height = 700

    p.drawString(100, 750, "Список покупок")
    for i, (name, data) in enumerate(ingr_list.items(), start=1):
        p.drawString(
            80, height, f"{i}. {name} – {data['amount']} {data['unit']}"
        )
        height -= 25
    p.showPage()
    p.save()

    return response
