theme
{
	name = "modern"

	view = view.small

	background
	{
		color = #2d3a44ff
		opacity = 100
	}

	item
	{
		opacity = 100

		prefix = 1

		text
		{
			normal = #ffffff
			select = #ffffff
			normal-disabled = #c0c0c0
			select-disabled = #a9a9a9
		}

		back
		{
			select = rgba(5, 19, 26, 1) // mantido
			select-disabled = #182c3eff // contraste melhorado sobre #586354
		}
	}

	// font
	// {
	// 	size = 14
	// 	name = "Segoe UI Variable Text"
	// 	weight = 2
	// 	italic = 0
	// }

	border
	{
		enabled = true
		size = 1
		color = #dcdcdc // menos brilhante que branco puro para reduzir brilho
		opacity = 100
		radius = 2
	}

	shadow
	{
		enabled = true
		size = 5
		opacity = 10 // leve aumento para mais definição
		color = #0d0d12 // mais escuro que #11111b
	}

	separator
	{
		size = 0.4
		color = #d2c5c2 // contraste mais sutil que o #e8dbd8
	}

	symbol
	{
		normal = #f0f0f0 // melhor contraste que #ffffff
		select = #d2a0a0 // mais claro que #b19292
		normal-disabled = #a9a9a9
		select-disabled = #8c7a7a
	}

	image
	{
		enabled = true
		color = [#c2c0b5, #ffffff, #1e1e2e] // leve clareamento na primeira cor
	}
}
