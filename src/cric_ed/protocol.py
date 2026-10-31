"""Small information-boundary/evaluation primitives for future CRIC-ED runs."""
import math
import random

def group_folds(group_ids, n_splits, seed):
    """Return (context_indices, query_indices); every group is queried once."""
    unique=list(dict.fromkeys(group_ids))
    if not 2 <= n_splits <= len(unique):
        raise ValueError('Need at least one distinct group per fold, with K >= 2')
    random.Random(seed).shuffle(unique)
    assigned={g:i % n_splits for i,g in enumerate(unique)}
    return [(tuple(i for i,g in enumerate(group_ids) if assigned[g]!=fold),
             tuple(i for i,g in enumerate(group_ids) if assigned[g]==fold)) for fold in range(n_splits)]

def topk_metrics(scores, error_labels, budget):
    """Evaluate a fixed eligible-cell universe. Larger score = more suspicious.

    Stable original cell order breaks ties; budget is never inferred from truth.
    No-positive recall is undefined and reported as None, not a perfect score.
    """
    if len(scores)!=len(error_labels) or not scores: raise ValueError('Aligned nonempty vectors required')
    if any(v not in (0,1) for v in error_labels): raise ValueError('Binary truth required')
    if any(not math.isfinite(s) for s in scores): raise ValueError('Nonfinite score: apply explicit failure policy')
    if isinstance(budget,bool) or not isinstance(budget,int) or not 0 <= budget <= len(scores):
        raise ValueError('Integer budget must be inside eligible-cell universe')
    selected=sorted(range(len(scores)),key=lambda i:(-scores[i],i))[:budget]
    tp=sum(error_labels[i] for i in selected); positives=sum(error_labels)
    precision=tp/budget if budget else None
    recall=tp/positives if positives else None
    f1=2*tp/(budget+positives) if budget+positives else None
    return {'budget':budget,'eligible_cells':len(scores),'true_positives':tp,'positives':positives,
            'precision':precision,'recall':recall,'f1':f1,'selected_indices':selected}
