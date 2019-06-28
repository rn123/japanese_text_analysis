import plotly.graph_objs as go


def word_distributions(word_list=None, word_level_statistics=None):
    positions = [word_level_statistics.word_pos[word] for word in word_list]
    keywords_in_context = [' '.join(word_level_statistics.tokens[n-2:n+3]) for n,w in enumerate(word_level_statistics.tokens)]

    word_list.reverse()
    positions.reverse()

    fig = go.FigureWidget()
    for w, p in zip(word_list, positions):
        scatter = fig.add_scatter(x=p, y=[w]*len(p))
        scatter.mode = 'markers'
        scatter.marker.symbol = 'line-ns-open'
        scatter.marker.color = 'grey'
        scatter.name = w
        scatter.hovertext = [keywords_in_context[n] for n in p]
        scatter.hoverinfo = 'text'

    ticklabels = []
    for n in range(1,55):
        if n%2 == 0:
            ticklabels.append(str(n))
        else:
            ticklabels.append('')

    layout = go.Layout(
        title='Word Distributions for {} Significant Terms'.format(len(word_list)),
        showlegend=False,
        autosize=True,
    #     width=1000,
        height=700,
        margin=go.layout.Margin(
            l=50,
            r=50,
            b=100,
            t=100,
            pad=4
        ),
    #     paper_bgcolor='#7f7f7f',
    #     plot_bgcolor='#c7c7c7',
        xaxis=dict(
            title=None,
            titlefont=dict(
                family='Arial, sans-serif',
                size=18,
                color='lightgrey'
            ),
            showticklabels=True,
    #         ticks='outside',
            tickangle=45,
            tickfont=dict(
                family='Old Standard TT, serif',
                size=14,
                color='black'
            ),
            # tickvals=chapter_boundaries,
            # ticktext=ticklabels,
            automargin=True,
            showgrid=True,
            zeroline=False,
            showline=False,
        ),
        yaxis=dict(
            title=None,
            titlefont=dict(
                family='Arial, sans-serif',
                size=18,
                color='lightgrey'
            ),
            showticklabels=True,
            automargin=True,
            tickangle=0,
            tickfont=dict(
                family='Old Standard TT, serif',
                size=14,
                color='black'
            ),
            tickvals=word_list,
            showgrid=True,
            zeroline=False,
            showline=False,
        )
    )

    fig.layout = layout
    fig.layout.hovermode = 'closest'

    return fig