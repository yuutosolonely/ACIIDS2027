import math
import pytest
from cric_ed.protocol import group_folds, topk_metrics

def test_group_context_never_contains_query_entity():
    ids=['a','a','b','c','c','d','e']
    folds=group_folds(ids,3,42)
    queried=[]
    for context,query in folds:
        assert set(context).isdisjoint(query)
        assert {ids[i] for i in context}.isdisjoint({ids[i] for i in query})
        assert set(context)|set(query)==set(range(len(ids)))
        queried.extend(query)
    assert sorted(queried)==list(range(len(ids)))
    assert folds==group_folds(ids,3,42)

def test_fixed_audit_budget_and_known_counts():
    m=topk_metrics([.9,.8,.7,.1],[1,0,1,0],2)
    assert (m['true_positives'],m['precision'],m['recall'],m['f1'])==(1,.5,.5,.5)
    assert m['eligible_cells']==4

def test_ties_use_fixed_order_not_truth():
    assert topk_metrics([1,1,1],[0,1,1],1)['selected_indices']==[0]

@pytest.mark.parametrize('budget',[-1,4,True,.5])
def test_invalid_budget_is_not_clamped(budget):
    with pytest.raises(ValueError): topk_metrics([1,2,3],[0,1,0],budget)

def test_nonfinite_predictions_are_not_silently_dropped():
    with pytest.raises(ValueError): topk_metrics([math.nan,1],[1,0],1)

def test_no_errors_has_undefined_recall():
    m=topk_metrics([2,1],[0,0],1)
    assert m['recall'] is None and m['precision']==0

def test_insufficient_groups_fail():
    with pytest.raises(ValueError): group_folds(['a','a'],2,0)
