from django.urls import path
from . import views

urlpatterns = [
	#Leave as empty string for base url
 	path('',views.main,name="main"),
  	path('signin',views.signin,name='signin'),
    path('regi',views.regi,name='regi'),
    
	path('store/', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),

	path('update_item/', views.updateItem, name="update_item"),
]